import os
import json
import faiss
import tiktoken
import openai
import numpy as np
from dotenv import load_dotenv

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import re
# Cargar API Key de OpenAI
load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")
DATABASE_URL = os.getenv("DATABASE_URL")
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Ruta absoluta de la carpeta index
CARPETA_INDEX = "index"
TAMANO_CHUNK = 700
SUPERPOSICION = 40
MODELO_EMBEDDING = "text-embedding-3-small"

# Inicializar tokenizer compatible con OpenAI
tokenizer = tiktoken.get_encoding("cl100k_base")

# Crear cliente
from openai import OpenAI
client = OpenAI()

def dividir_en_chunks(texto, tamano_chunk, superposicion):
    # convetimos a codigo binario
    tokens = tokenizer.encode(texto)
    chunks = []
    i = 0
    while i < len(tokens):
        sub_tokens = tokens[i:i+tamano_chunk]
        chunk = tokenizer.decode(sub_tokens)
        chunks.append(chunk)
        i += tamano_chunk - superposicion
    return chunks

def limpiar_texto(texto: str) -> str:
    return re.sub(r'[\x00-\x08\x0B-\x0C\x0E-\x1F]', '', texto)

def generar_embedding(texto):
    if not texto.strip():
        return None
    try:
        response = client.embeddings.create(
            model=MODELO_EMBEDDING,
            input=texto
        )
        return response.data[0].embedding
    except Exception as e:
        print(f"❌ Error generando embedding: {e}")
        return None
    
def guardar_index(nombre_base, vectores, metadata):
    dimension = len(vectores[0])
    index = faiss.IndexFlatL2(dimension)
    index.add(np.array(vectores).astype("float32"))

    ruta_index = os.path.join(CARPETA_INDEX, f"{nombre_base}.index")
    faiss.write_index(index,ruta_index)

    ruta_meta = os.path.join(CARPETA_INDEX, f"{nombre_base}.json")
    with open(ruta_meta,"w", encoding="utf-8") as f:
        json.dump(metadata,f,ensure_ascii=False)
    
    print(f"✅ Guardado index: {ruta_index}")
    print(f"✅ Guardado metadata: {ruta_meta}")

  

def procesar_archivo_db(nombre_archivo, paginas):

    session = SessionLocal()
    try:
        archivo = ArchivoResumen(nombre_archivo= nombre_archivo)
        session.add(archivo)
        session.commit()
        session.refresh(archivo)

        vectores = []

        #procesar cada pagina
        for pagina in paginas:
            texto = pagina["texto"]
            num_pag = pagina["pagina"]
            chunks = dividir_en_chunks(texto,TAMANO_CHUNK, SUPERPOSICION)
            for chunk in chunks:
                chunk_limpio = limpiar_texto(chunk)
                embedding = generar_embedding(chunk_limpio)
                if embedding is not None:
                    embedding = np.array(embedding, dtype=np.float32)
                    doc = DocumentoEmbeddingResumen(
                        id_archivo = archivo.id,
                        texto = chunk_limpio,
                        embedding = embedding.tolist(),
                        num_pag = num_pag
                    )
                    session.add(doc)
                    vectores.append(embedding)
        session.commit()
        if vectores:
            vector_avg = np.mean(vectores, axis=0, dtype=np.float32)
            archivo.vector_promedio = vector_avg.tolist()
            session.commit()
        print(f"✅ Archivo '{nombre_archivo}' y sus embeddings guardados en la base de datos.")

    except Exception as e:
        session.rollback()
        print(f"Error al prcesar archivos :{e}") 



# archivos_promedio_cache = []

# def cargar_archivos_memoria():
#     print("guardando en memoria")
#     global archivos_promedio_cache
#     session = SessionLocal()
#     query = text("SELECT id,nombre_archivo,vector_promedio FROM archivos")
#     resultados = session.execute(query).fetchall()
    
#     archivos_promedio_cache = [
#         {
#             "id": r.id,
#             "nombre": r.nombre_archivo,
#             "vector": np.array(json.loads(r.vector_promedio), dtype=np.float32)
#         }for r in resultados
#     ]
#     print(f"{len(archivos_promedio_cache)} cargados en memoria")

# def vector_promedio(nombre_archivo):
#     ruta_index = os.path.join(CARPETA_INDEX,f"{nombre_archivo}.index")
#     ruta_salida = os.path.join(CARPETA_INDEX, f"{nombre_archivo}_vector.npy")    
#     index = faiss.read_index(ruta_index)
#     vectores = index.reconstruct_n(0, index.ntotal)

#     vector_promedio = np.mean(vectores, axis=0)
#     np.save(ruta_salida, vector_promedio)
#     print(f"Guardado: {ruta_salida}")

def indexar(nombre_archivo, paginas):
    procesar_archivo_db(nombre_archivo,paginas)
    



