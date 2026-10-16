Práctica: AWS Secrets Manager con Boto3

Programa en Python que recupera un secreto (usuario y contraseña ficticios) almacenado en AWS Secrets Manager usando Boto3, y que siempre obtiene la versión actual del secreto sin necesidad de modificar el código.

Objetivo
Tener un secreto de prueba con un usuario y una contraseña ficticios.
Restringir los permisos para que el programa solo pueda leer ese secreto.
Recuperar el secreto desde Python con Boto3.
Modificar el valor del secreto y comprobar que el mismo código obtiene la versión nueva.
Estructura del proyecto
.
├── Secrets Manager/
│   └── Secrets.py        # Script que recupera el secreto
├── requirements.txt      # Dependencias de Python
├── .env                  # Configuración local (NO se sube al repositorio)
└── README.md
Requisitos
Python 3.9 o superior
AWS CLI instalada y configurada
Un usuario o rol de AWS con permiso secretsmanager:GetSecretValue sobre el secreto
El secreto jah_secreto creado en la región us-east-2 (Ohio)
Instalación
bash
pip install -r requirements.txt

o, si solo necesitas Boto3:

bash
pip install boto3
Configuración de credenciales

Boto3 toma las credenciales de la cadena estándar de AWS (variables de entorno, perfil de aws configure o rol asociado). No se escriben llaves dentro del código.

bash
aws configure
# Default region name: us-east-2

Importante: nunca subas llaves de acceso ni el archivo .env al repositorio. Verifica que .env esté en el .gitignore.

El secreto

El secreto se llama jah_secreto y guarda un JSON con esta forma:

json
{
  "username": "usuario_prueba",
  "password": "<contraseña ficticia>"
}

Para crearlo (si no existe):

bash
aws secretsmanager create-secret \
  --name jah_secreto \
  --region us-east-2 \
  --secret-string '{"username":"usuario_prueba","password":"Clave-Falsa-123"}'
Permisos (principio de mínimo privilegio)

El programa solo necesita leer ese secreto. La política IAM mínima es:

json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": "secretsmanager:GetSecretValue",
      "Resource": "arn:aws:secretsmanager:us-east-2:<ID_CUENTA>:secret:jah_secreto-*"
    }
  ]
}

Con esta política, intentar leer cualquier otro secreto devuelve AccessDeniedException.

Ejecución

Como la carpeta tiene un espacio en el nombre, usa comillas:

bash
python "Secrets Manager/Secrets.py"

Salida esperada:

Usuario recuperado: <username>
Contraseña recuperada: <password>
Cómo comprobar que obtiene la versión actual
Ejecuta el script y anota la salida.
Modifica el valor del secreto:
bash
   aws secretsmanager put-secret-value \
     --secret-id jah_secreto \
     --region us-east-2 \
     --secret-string '{"username":"usuario_nuevo","password":"Clave-Rotada-456"}'
Ejecuta el mismo script, sin cambiarlo:
bash
   python "Secrets Manager/Secrets.py"

Ahora imprime el usuario y la contraseña nuevos.

Revisa las versiones del secreto:
bash
   aws secretsmanager list-secret-version-ids \
     --secret-id jah_secreto \
     --region us-east-2 \
     --no-cli-pager

Verás la versión nueva con la etiqueta AWSCURRENT y la anterior con AWSPREVIOUS.

Seguridad
Los datos del secreto son ficticios, solo para pruebas.
No se guardan credenciales en el código ni en el repositorio.
No imprimas contraseñas reales en consola ni en registros.
No publiques el ID de cuenta de AWS ni los ARN completos en repositorios públicos.
Solución de problemas
Error	Causa probable
ResourceNotFoundException	El secreto no existe en la región indicada (revisa us-east-2).
AccessDeniedException	Al usuario o rol le falta secretsmanager:GetSecretValue sobre el secreto.
NoCredentialsError	Boto3 no encuentra credenciales (revisa aws configure o el perfil activo).
ResourceExistsException	El secreto ya existe; usa put-secret-value para cambiar su valor.
python: can't open file ...	La ruta tiene espacios; escríbela entre comillas.
Tecnologías
Python
Boto3
AWS Secrets Manager
AWS IAM