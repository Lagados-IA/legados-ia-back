import json
import openai
from dotenv import load_dotenv
import os
from scripts.utilitarios.gestion_conocimiento.agente_selector import elegir_mejor_chunck
from scripts.utilitarios.prompts.promt import prompt_base
from scripts.editar_variables import MODELO,CHUNCKS_POR_DOCUMENTO,MODELO_MINI,MODELO_TRANSCRIBE,MODELO_TEXTO_AUDIO

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




import base64
import subprocess
import tempfile
# def generar_respuesta_audiod(user_id, nombre, file, historial):

    
#     # leer webm
#     webm_bytes = file.file.read()

   
#     with tempfile.NamedTemporaryFile(suffix=".webm", delete=False) as f_in:
#         f_in.write(webm_bytes)
#         webm_path = f_in.name

#     wav_path = webm_path.replace(".webm", ".wav")

#     subprocess.run(
#         ["ffmpeg", "-i", webm_path, "-ar", "44100", "-ac", "1", wav_path, "-y"],
#         check=True
#     )

#     with open(wav_path, "rb") as f:
#         wav_bytes = f.read()

#     encoded_audio = base64.b64encode(wav_bytes).decode("utf-8")

#      # TEXTO USUARIO
#     transcription = client.audio.transcriptions.create(
#         model= MODELO_TRANSCRIBE, 
#         file=("audio.wav", wav_bytes)
#     )

#     chunks = elegir_mejor_chunck(user_id, transcription.text,CHUNCKS_POR_DOCUMENTO)
#     contexto = "\n\n".join([f" Pregunta:{c['pregunta']} \n Respuesta:{c['respuesta']} \n" for c in chunks])

#     print(contexto)

#     prompt = prompt_base(nombre)

#     # HISTORIAL
#     mensajes = [
#         {"role":"system","content":prompt +f"\nMemoria: \n{contexto}"}
#     ]
    
#     for msg in historial:
#         mensajes.append({
#             "role":"user" if msg["rol"] == "user" else "assistant",
#             "content": msg["contenido"]
#         })
#     mensajes.append({
#         "role":"user",
#         "content":[
#             {"type":"text","text":"Aquí tienes mi nota de voz:"},
#             {
#                 "type":"input_audio",
#                 "input_audio":{
#                     "data":encoded_audio,
#                     "format":"wav"
#                 }
#             }
#         ]
#     })

#     # AUDIO
#     completion = client.chat.completions.create(
#         model=MODELO_AUDIO,
#         modalities=["text", "audio"],
#         audio={"voice": "onyx", "format": "wav"},
#         messages=mensajes
#     )

    


#     # TEXTO IA
#     mensaje_ia = completion.choices[0].message.audio.data
#     audio_bytes = base64.b64decode(mensaje_ia)

#     transcription_ia = client.audio.transcriptions.create(
#         model= MODELO_TRANSCRIBE, 
#         file=("audio.wav", audio_bytes ),
#         response_format="text"
#     )

    

#     texto_usuario = transcription.text
#     texto_ia =  transcription_ia
#     audio_ia = completion.choices[0].message.audio.data



#     return audio_ia, texto_ia, texto_usuario



def generar_respuesta_audio(user_id, nombre, file, historial): 
    # === 1) LEER WEBM DEL USUARIO === 
    webm_bytes = file.file.read() 
    # === 2) TRANSCRIBIR AUDIO DEL USUARIO === 
    transcription = client.audio.transcriptions.create( 
        model=MODELO_TRANSCRIBE, file=("audio.webm", webm_bytes) ) 
    texto_usuario = transcription.text 
    # === 3) OBTENER CONTEXTO Y ARMAR MENSAJES === 
    chunks = elegir_mejor_chunck(user_id, texto_usuario, CHUNCKS_POR_DOCUMENTO) 
    contexto = "\n\n".join([ f"Pregunta:{c['pregunta']}\nRespuesta:{c['respuesta']}" for c in chunks ]) 
    prompt = prompt_base(nombre) 
    mensajes = [{"role": "system", "content": prompt + f"\nMemoria:\n{contexto}"}] 
    for msg in historial: mensajes.append(
        { "role": "user" if msg["rol"] == "user" else "assistant", "content": msg["contenido"] }) 
    mensajes.append({"role": "user", "content": texto_usuario}) 
    # === 4) GENERAR RESPUESTA EN TEXTO (GPT-4.1) === 
    completion = client.chat.completions.create( model=MODELO_MINI, messages=mensajes ) 
    texto_ia = completion.choices[0].message.content 
    tts = client.audio.speech.create( model=MODELO_TEXTO_AUDIO, voice="onyx", input=texto_ia ) 
    audio_ia = tts.read() 
    audio_b64 = base64.b64encode(audio_ia).decode("utf-8") 
    # === 6) RETORNAR TODA LA DATA === 
    return audio_b64, texto_ia, texto_usuario

# def generar_respuesta_audio(user_id, nombre, file, historial):

#     transcription = client.audio.transcriptions.create(
#         model=MODELO_TRANSCRIBE,
#         file=("audio.webm", file)
#     )
#     texto_usuario = transcription.text
#     yield f"event:transcripcion\ndata:{texto_usuario}\n\n"

#     # === 3) CONTEXTO Y MENSAJES ===
#     chunks = elegir_mejor_chunck(user_id, texto_usuario, CHUNCKS_POR_DOCUMENTO)
#     contexto = "\n\n".join([
#         f"Pregunta:{c['pregunta']}\nRespuesta:{c['respuesta']}" 
#         for c in chunks
#     ])

#     prompt = prompt_base(nombre)

#     mensajes = [{"role": "system", "content": prompt + f"\nMemoria:\n{contexto}"}]

#     for msg in historial:
#         mensajes.append({
#             "role": "user" if msg["rol"] == "user" else "assistant",
#             "content": msg["contenido"]
#         })

#     mensajes.append({"role": "user", "content": texto_usuario})
#     texto_ia=""
    
#     completion_stream = client.chat.completions.create(
#         model=MODELO_MINI,
#         messages=mensajes,
#         stream=True
#     )
    
#     for chunk in completion_stream:
#         delta = chunk.choices[0].delta.content
#         if delta:
#             texto_ia += delta
#             yield f"event:texto\ndata:{delta}\n\n"

#     # === 5) TTS FINAL ===
#     tts = client.audio.speech.create(
#         model=MODELO_TEXTO_AUDIO,
#         voice="onyx",
#         input=texto_ia
#     )
#     audio_ia = tts.read()
#     audio_b64 = base64.b64encode(audio_ia).decode("utf-8")

#     yield f"event:audio\ndata:{audio_b64}\n\n"
#     yield f"event:end\ndata:done\n\n"




