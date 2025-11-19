from openai import OpenAI
import openai
import os
from dotenv import load_dotenv
load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")
# Obtener lista de modelos
from openai import OpenAI
client = OpenAI()
modelos = client.models.list()

# Imprimirlos
for modelo in modelos.data:
    print(modelo.id)
