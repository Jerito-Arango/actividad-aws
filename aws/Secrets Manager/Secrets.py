import boto3
import json

# Inicializar el cliente en la región correcta (us-east-2)
client = boto3.client('secretsmanager', region_name='us-east-2')

# Recuperar el secreto por su nombre o ARN
response = client.get_secret_value(SecretId='jah_secreto')

# Convertir el string JSON a diccionario de Python
secret_data = json.loads(response['SecretString'])

# Imprimir los datos del secreto
print("Usuario recuperado:", secret_data.get('username'))
print("Contraseña recuperada:", secret_data.get('password'))