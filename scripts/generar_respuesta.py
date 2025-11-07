import json
import openai
from dotenv import load_dotenv
import os
from scripts.utilitarios.gestion_conocimiento.agente_selector import elegir_mejor_chunck
from scripts.utilitarios.prompts.promt import prompt_base
from scripts.editar_variables import MODELO,CHUNCKS_POR_DOCUMENTO

import re
# Cargar clave desde .env
load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

# Cliente de OpenAI
from openai import OpenAI
client = OpenAI()





def generar_respuesta_stream(user_id,nombre,pregunta_usuario, historial):
    
    chunks = elegir_mejor_chunck(user_id,pregunta_usuario,CHUNCKS_POR_DOCUMENTO)

    contexto = "\n\n".join([f" Pregunta:{c['pregunta']} \n Respuesta:{c['respuesta']} \n" for c in chunks])
    print(contexto)
    modelo = MODELO
    prompt = prompt_base(nombre)

    if chunks == []:
        mensajes = [
            {
                "role": "system",
                "content": "Responde exactamente: Lo siento, aún no he cargado información a mi legado"
            }
        ]
    else:
        

        mensajes = [
            {
                "role": "system",
                "content": prompt  + f"\nMemoria: \n{contexto}"
            }
        ]

    mensajes.extend({
        "role": "user" if msg.rol == "user" else "assistant",
        "content": msg.contenido
    } for msg in historial)

    # Generator para streaming
    def event_generator():
        with client.chat.completions.stream(model=modelo, messages=mensajes) as stream:
            for event in stream:
                if hasattr(event, "delta") and event.delta:
                    yield json.dumps({"contenido": event.delta}) + "\n"

    return event_generator


