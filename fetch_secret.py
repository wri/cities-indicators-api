import boto3
import os
import sys

def get_secret(secret_name, region_name="us-east-1"):
    client = boto3.client("secretsmanager", region_name=region_name)
    
    try:
        response = client.get_secret_value(SecretId=secret_name)
        if "SecretString" in response:
            return response["SecretString"]
        else:
            return response["SecretBinary"]
    except Exception as e:
        print(f"Erro ao recuperar segredo: {str(e)}")
        sys.exit(1)

secret_name = "airtable-api-key-value-ogq3dA"
api_key = get_secret(secret_name)

os.environ["AIRTABLE_API_KEY"] = api_key

print("API Key carregada com sucesso!")
