import os
import openai
from dotenv import load_dotenv
load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

# Cliente de OpenAI
from openai import OpenAI
client = OpenAI()

def conexion_gpt_normal(modelo, mensajes):
    
    respuesta = client.chat.completions.create(
            model=modelo,
            messages=mensajes,
    )
    tokens = respuesta.usage.total_tokens if respuesta.usage else 0
    contenido = respuesta.choices[0].message.content
    return contenido, tokens