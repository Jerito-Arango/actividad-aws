import boto3
import time

# Configurar región
REGION = 'us-east-1'

# Inicializar clientes
s3_client = boto3.client('s3', region_name=REGION)
ec2_client = boto3.client('ec2', region_name=REGION)
rds_client = boto3.client('rds', region_name=REGION)

def crear_infraestructura():
    print("1. Creando Bucket de S3...")
    bucket_name = "lab-boto3-bucket-de-gr01-user-10"
    try:
        s3_client.create_bucket(Bucket=bucket_name)
        print(f"Bucket {bucket_name} creado exitosamente.")
    except Exception as e:
        print(f"Error creando bucket: {e}")

    print("2. Creando VPC y red...")
    # Crear VPC
    vpc_response = ec2_client.create_vpc(CidrBlock='10.0.0.0/16')
    vpc_id = vpc_response['Vpc']['VpcId']
    ec2_client.create_tags(Resources=[vpc_id], Tags=[{'Key': 'Name', 'Value': 'VPC-Boto3'}])
    print(f"VPC creada con ID: {vpc_id}")

    # Habilitar nombres DNS en la VPC
    ec2_client.modify_vpc_attribute(VpcId=vpc_id, EnableDnsHostnames={'Value': True})

    # Crear Subred 1
    subnet1_response = ec2_client.create_subnet(VpcId=vpc_id, CidrBlock='10.0.1.0/24', AvailabilityZone=f'{REGION}a')
    subnet1_id = subnet1_response['Subnet']['SubnetId']
    print(f"Subred 1 creada: {subnet1_id}")

    # Crear Subred 2 (necesaria para RDS)
    subnet2_response = ec2_client.create_subnet(VpcId=vpc_id, CidrBlock='10.0.2.0/24', AvailabilityZone=f'{REGION}b')
    subnet2_id = subnet2_response['Subnet']['SubnetId']
    print(f"Subred 2 creada: {subnet2_id}")

    # Crear Internet Gateway y asociarlo
    igw_response = ec2_client.create_internet_gateway()
    igw_id = igw_response['InternetGateway']['InternetGatewayId']
    ec2_client.attach_internet_gateway(InternetGatewayId=igw_id, VpcId=vpc_id)
    print(f"Internet Gateway creado y asociado: {igw_id}")

    # Crear Grupo de Seguridad para EC2
    sg_response = ec2_client.create_security_group(
        GroupName='ec2-boto3-sg',
        Description='Grupo de seguridad desde Boto3',
        VpcId=vpc_id
    )
    sg_id = sg_response['GroupId']
    ec2_client.authorize_security_group_ingress(
        GroupId=sg_id,
        IpPermissions=[{
            'IpProtocol': 'tcp',
            'FromPort': 22,
            'ToPort': 22,
            'IpRanges': [{'CidrIp': '0.0.0.0/0'}]
        }]
    )
    print(f"Grupo de seguridad creado: {sg_id}")

    print("3. Lanzando instancia EC2...")
    instance_response = ec2_client.run_instances(
        ImageId='ami-0c7217cdde317cfec',
        InstanceType='t2.micro',
        MinCount=1,
        MaxCount=1,
        NetworkInterfaces=[{
            'SubnetId': subnet1_id,
            'DeviceIndex': 0,
            'AssociatePublicIpAddress': True,
            'Groups': [sg_id]
        }],
        TagSpecifications=[{
            'ResourceType': 'instance',
            'Tags': [{'Key': 'Name', 'Value': 'ServidorBoto3'}]
        }]
    )
    instance_id = instance_response['Instances'][0]['InstanceId']
    print(f"Instancia EC2 lanzada con ID: {instance_id}")

    print("4. Creando base de datos RDS...")
    # Crear grupo de subredes para RDS
    try:
        rds_client.create_db_subnet_group(
            DBSubnetGroupName='db-subnet-group-boto3',
            DBSubnetGroupDescription='Subnet group para RDS desde Boto3',
            SubnetIds=[subnet1_id, subnet2_id]
        )
    except Exception as e:
        print(f"Nota sobre db-subnet-group: {e}")

    # Crear RDS administrando la contraseña en Secrets Manager
    rds_client.create_db_instance(
        DBInstanceIdentifier='mirdsboto3',
        Engine='mysql',
        EngineVersion='8.0',
        DBInstanceClass='db.t3.micro',
        AllocatedStorage=20,
        MasterUsername='adminuser',
        ManageMasterUserPassword=True,
        DBSubnetGroupName='db-subnet-group-boto3'
    )
    print("Instancia RDS en proceso de creación (esto puede tomar unos minutos)...")

if __name__ == "__main__":
    crear_infraestructura()