import boto3
import os
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

rekognition = boto3.client(
    "rekognition",
    aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
    aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
    region_name=os.getenv("AWS_REGION")
)

# Probar listar colecciones
response = rekognition.list_collections()
print("Colecciones existentes:", response.get("CollectionIds", []))
