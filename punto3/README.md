Conexión a DocumentDB

DocumentDB no permite conexiones desde internet, por lo que el computador se conecta a través de la EC2, que sí está dentro de la VPC:

PC (WSL, Compass y Python)
   │  Túnel SSH: localhost:27018 → EC2:22
   ▼
EC2 t3.micro (subred pública, sg-ec2-tunnel: SSH 22 solo desde mi IP)
   │  TCP 27017 + TLS
   ▼
Clúster DocumentDB (misma VPC, sg-docdb: 27017 solo desde sg-ec2-tunnel)

AWS Secrets Manager ──► contraseña, leída desde Python con boto3
Grupos de seguridad: sg-ec2-tunnel solo permite SSH (puerto 22) desde mi IP. sg-docdb solo permite el puerto 27017 con origen el grupo sg-ec2-tunnel, es decir, solo la EC2 puede hablar con la base de datos.
Túnel SSH: ssh -i key-pair-docdb.pem -N -L 27017:docdb-2026-10-16-13-49-19-jah1.cluster-cni0hmtynfvx.us-east-1.docdb.amazonaws.com:27017 ec2-user@100.53.2.148. 
TLS y certificado: se descargó el paquete de certificados de AWS (global-bundle.pem) y se indicó en Compass y en PyMongo (tlsCAFile). Como el certificado está emitido para el nombre del clúster y no para localhost, se activó tlsAllowInvalidHostnames. La validación de la autoridad certificadora se mantiene.
Compass: conexión a localhost:27017 con Direct Connection, usuario y contraseña, TLS activado y el archivo de certificado.
Python: PyMongo se conecta al mismo puerto del túnel, con las mismas opciones de TLS.


Manejo de la contraseña con Secrets Manager

La contraseña del usuario administrador (docdbadmin, fue la que puse desde la página de aws) la genera y guarda AWS Secrets Manager al crear el clúster, por lo que nunca se escribe en el código ni en los archivos del repositorio. El programa en Python la recupera al ejecutarse con boto3:

python
sm = boto3.client("secretsmanager", region_name="us-east-1")
secret = json.loads(sm.get_secret_value(SecretId=SECRET_NAME)["SecretString"])
El usuario IAM que ejecuta el programa necesita el permiso secretsmanager:GetSecretValue sobre ese secreto.
Si la contraseña se rota o cambia, el programa obtiene la nueva sin modificar el código.
Las llaves de acceso de AWS (necesarias para llamar a Secrets Manager) se guardan con aws configure, no en el código.


El script docdb.py se conecta a través del túnel SSH y ejecuta lo siguiente sobre la base de datos escuela, colección estudiantes:

Inserta 10 documentos con insert_many.
Filtro: estudiantes con promedio >= 4.0, con find.
Ordenación: todos los estudiantes por promedio descendente, con sort.
Agregación: cantidad de estudiantes y promedio general por carrera, con aggregate y $group.