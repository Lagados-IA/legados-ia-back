import json
import openai
from dotenv import load_dotenv
import os
import numpy as np
from scripts.agente_selector import elegir_mejor_json_por_embedding
from scripts.apis_gpt.api_base import conexion_gpt_normal
from scripts.prompts.promt import prompt_base
from scripts.utilitarios.optener_documentos import obtener_documentos
from scripts.utilitarios.ml.correcciones import buscar_correccion
from scripts.utilitarios.ml.feedback import procesar_feedback

import re
# Cargar clave desde .env
load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

# Cliente de OpenAI
from openai import OpenAI
client = OpenAI()

from .utilitarios.embedding import generar_embedding
from scripts.utilitarios.limpia_ruta import limpiar_ruta
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
from sqlalchemy import text


DATABASE_URL = "postgresql://ingenieros_user:RPN3vIieAiYqSfWe85RoiY8z8IMNj4nK@dpg-d2nhqb95pdvs73bvh8f0-a.oregon-postgres.render.com/ingenieros"
engine = create_engine(DATABASE_URL)
Session_local = sessionmaker(bind=engine)

# Función para buscar chunks más parecidos
# def buscar_similares(pregunta, cantidad, id_archivo,nombre_archivo):

#     session = Session_local()
    
#     try:
#         embedding = generar_embedding(pregunta)
#         if isinstance(embedding, np.ndarray):
#             embedding = embedding.tolist()
        
        
#         query = text(f"""
#             SELECT id, texto, num_pag, embedding <-> (:pregunta)::vector AS distancia
#             FROM documentos_embedding
#             WHERE id_archivo = :id_archivo
#             ORDER BY distancia ASC
#             LIMIT :cantidad
#         """)

#         resultados = session.execute(
#             query,
#             {"pregunta":embedding, "id_archivo": id_archivo, "cantidad":cantidad}
#         ).fetchall()
#         #converir a diccionario
#         chunks = [
#             {
#                 "pagina": r.num_pag,
#                 "ruta": nombre_archivo, 
#                 "texto": r.texto
#             }
#             for r in resultados
#         ]

#         return chunks


#     except Exception as e:
#         print(f"❌ Error en buscar_similares: {e}")
#         return []


def buscar_similares(pregunta, cantidad, id_archivo,nombre_archivo):

    session = Session_local()
    
    try:
        embedding = generar_embedding(pregunta)
        
        if isinstance(embedding, np.ndarray):
            embedding = [float(x) for x in embedding]
        
        session.execute(text("SET enable_seqscan = OFF;"))
        session.execute(text("SET hnsw.ef_search = 50;"))
        query = text(f"""
            SELECT  texto, num_pag
            FROM documentos_embedding_resumen
            WHERE id_archivo = :id_archivo
            ORDER BY embedding  <-> (:pregunta)::vector
            LIMIT :cantidad
        """)

        resultados = session.execute(
            query,
            {"pregunta":embedding, "id_archivo": id_archivo, "cantidad":cantidad}
        ).fetchall()
        #converir a diccionario
        chunks = [
            {
                "pagina": r.num_pag,
                "ruta": nombre_archivo, 
                "texto": r.texto
            }
            for r in resultados
        ]

        return chunks


    except Exception as e:
        print(f"❌ Error en buscar_similares: {e}")
        return []


def extraer_ultima_pregunta(texto:str)-> str:
    preguntas = re.findall(r"[^\n.?!]*\?", texto)
    return preguntas[-1].strip() if preguntas else ""

def formatear_historial(historial):
    contexto_historial =[]

    for mensaje in historial:
        if mensaje.rol == "usuario":
            contexto_historial.append(f"Usuario: {mensaje.contenido}")
        elif mensaje.rol== "bot":
             # Extraer solo la última pregunta de la respuesta completa del bot
            ultima_pregunta = extraer_ultima_pregunta(mensaje.contenido)
            if ultima_pregunta:
                contexto_historial.append(f"Bot: {ultima_pregunta}")
    return "\n".join(contexto_historial)





# Función para generar respuesta usando OpenAI
def generar_respuesta(pregunta_usuario,historial):

    procesar_feedback(historial)
    # elegir archivo vectorial(base de datos)
    
    archivos_existentes = obtener_documentos()
    #agentes = elegir_todos_los_agentes()
    chunks = []
    agentes = []

    # respuesta_correccion = buscar_correccion(pregunta_usuario)
    # if respuesta_correccion:
    #     chunks.append({
    #          "pagina":"",
    #          "ruta": "",
    #          "texto": respuesta_correccion
    #     })
    # else:
    agentes = elegir_mejor_json_por_embedding(pregunta_usuario,top_k=2)
    for agente in agentes:
            chunks.extend(buscar_similares(pregunta_usuario, 4,agente["id"],agente["nombre"]))
    
    # Unir los chunks para enviar a GPT
    contexto = "\n\n".join([f"(Pág. {c['pagina']}) | Doc: {c['ruta']}:\n {c['texto']} \n" for c in chunks])
    # obtenemos solo lo que el usuario a dicho
    #historial_conversacion = formatear_historial(historial)
    modelo =  'gpt-4.1'
    mensajes = []
    prompt = prompt_base()
    mensajes.append({
        "role":"system",
        "content":prompt + "lista de documento, en BD\n"+ "\n".join(archivos_existentes) +f"\nFuentes encontradas:\n{contexto}"
    })


    #print
    print("\n📄 Chunks seleccionados:\n")
    for c in chunks:
        print(f"📌 Pág. {c['pagina']} | Doc: {c['ruta']}:\n -> {c['texto']}\n{'-'*80}")



    mensajes.extend({
            "role":"user" if msg.rol == "usuario" else "assistant",
            "content": msg.contenido
        } for msg in historial)
    
    contenido,tokens = conexion_gpt_normal(modelo, mensajes)

    return contenido, modelo, tokens


def generar_respuesta_stream(pregunta_usuario, historial):
    # Igual que generar_respuesta, pero no llamamos a conexion_gpt_normal
    #procesar_feedback(historial)
    agentes = elegir_mejor_json_por_embedding(pregunta_usuario, top_k=2)
    archivos_existentes = obtener_documentos()
    chunks = []
    
    for agente in agentes:
        chunks.extend(buscar_similares(pregunta_usuario, 4, agente["id"], agente["nombre"]))

    contexto = "\n\n".join([f"(Pág. {c['pagina']}) | Doc: {c['ruta']}:\n {c['texto']} \n" for c in chunks])

    modelo = "gpt-4.1"
    prompt = prompt_base()
    mensajes = [
        {
            "role": "system",
            "content": prompt + "lista de documento, en BD\n" + "\n".join(archivos_existentes) + f"\nFuentes encontradas:\n{contexto}"
        }
    ]
    mensajes.extend({
        "role": "user" if msg.rol == "usuario" else "assistant",
        "content": msg.contenido
    } for msg in historial)

    # Generator para streaming
    def event_generator():
        with client.chat.completions.stream(model=modelo, messages=mensajes) as stream:
            for event in stream:
                if hasattr(event, "delta") and event.delta:
                    yield json.dumps({"texto": event.delta}) + "\n"

    return event_generator


