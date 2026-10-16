# Laboratorio de Automatización e Infraestructura en AWS

Este repositorio contiene la documentación, scripts y archivos de configuración utilizados para el despliegue, gestión y eliminación de una arquitectura en la nube de AWS (incluyendo EC2, S3, RDS, VPC y componentes de red). El proyecto se desarrolló comparando tres enfoques diferentes: **Terraform**, **AWS CLI** y **Python (Boto3)**.

---

##  Tecnologías y Herramientas Utilizadas
* **AWS Management Console** para validación visual de recursos.
* **AWS CLI** para la ejecución de comandos en la terminal y gestión mediante la API.
* **Terraform** como herramienta de Infraestructura como Código (IaC).
* **Python (Boto3)** para la automatización programática del despliegue.

---

## Estructura del Proyecto
* `main.tf`: Archivo principal de configuración y declaración de recursos para Terraform.
* `deploy_boto3.py`: Script en Python utilizando la librería Boto3 para automatizar la creación de la infraestructura.
* `documento_evidencias.md`: Registro visual y explicativo de los comandos ejecutados y las respuestas de la terminal.

---

##  Fases del Laboratorio

1. **Definición y Planificación:** 
   Se diseñó la arquitectura estableciendo los bloques de red (VPC, subredes, tablas de rutas e Internet Gateway), una instancia EC2, un bucket de S3 y una base de datos RDS con credenciales gestionadas de manera segura.
   
2. **Despliegue Multiherramienta:** 
   * **Terraform:** Se inicializó el directorio, se ejecutó `terraform apply` para aprovisionar toda la infraestructura de forma automatizada y se validó con `terraform plan`.
   * **Python (Boto3):** Se ejecutó el script de automatización para desplegar los servicios programáticamente.
   * **AWS CLI:** Se utilizaron comandos nativos de la terminal para realizar llamadas directas a la API de AWS y configurar la red y los servicios de forma granular.

3. **Seguridad y Autenticación:** 
   Las herramientas se autenticaron mediante un usuario IAM dedicado (`user_cli`) utilizando llaves de acceso locales. Se evitó almacenar llaves de acceso en Secrets Manager debido a la dependencia circular de autenticación, y se protegió el archivo de estado de Terraform (`terraform.tfstate`) para no exponer datos sensibles.

4. **Limpieza y Costos:** 
   Para evitar cobros innecesarios en la cuenta compartida, se procedió a terminar la instancia EC2, eliminar la base de datos RDS, vaciar y borrar el bucket de S3, y limpiar los componentes de red y la VPC siguiendo el orden estricto de dependencias de AWS.