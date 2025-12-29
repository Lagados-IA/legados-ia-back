import os
import numpy as np
from scripts.utilitarios.embedding.embedding import generar_embedding  # Usa tu función existente
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv
load_dotenv()
# Config DB
VECTORES_CACHE = None
DATABASE_URL = os.getenv("DATABASE_URL")
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)

def elegir_mejor_chunck(user_id, pregunta, cantidad_chunks):

    session = SessionLocal()
    
    try:
        embedding = generar_embedding(pregunta)
        
        if isinstance(embedding, np.ndarray):
            embedding = [float(x) for x in embedding]
        vector_cero = [0.0]*1536
        

        
        query = text("""
            SELECT respuesta, pregunta
            FROM chunks
            WHERE id_persona = :id_persona
              AND (embedding <=> (:vector_cero)::vector) IS DISTINCT FROM 0
              AND trim(coalesce(respuesta, '')) <> ''     -- evita respuestas vacías
            ORDER BY embedding <=> (:pregunta)::vector
            LIMIT :cantidad
        """)
       


        resultados = session.execute(
            query,
            {"id_persona":user_id, "pregunta":embedding,"cantidad":cantidad_chunks,"vector_cero":vector_cero}
        ).fetchall()
        if not resultados:
            return []
        #converir a diccionario
        chunks = [
            {
                "respuesta": r.respuesta,
                "pregunta": r.pregunta
            }
            for r in resultados
        ]

        return chunks


    except Exception as e:
        print(f"❌ Error en buscar_similares: {e}")
        return []
    finally:
        session.close()



def elergir_chunk_libro(user_id, pregunta, cantidad_chunks):

    session = SessionLocal()
    
    try:
        embedding = generar_embedding(pregunta)
        
        if isinstance(embedding, np.ndarray):
            embedding = [float(x) for x in embedding]
        vector_cero = [0.0]*1536
        

        
        query = text("""
            SELECT libro,contenido
            FROM document_chunks
            WHERE id_persona = :id_persona
              AND (embedding <=> (:vector_cero)::vector) IS DISTINCT FROM 0
              AND trim(coalesce(contenido, '')) <> ''    
            ORDER BY embedding <=> (:pregunta)::vector
            LIMIT :cantidad
        """)
       


        resultados = session.execute(
            query,
            {"id_persona":user_id, "pregunta":embedding,"cantidad":cantidad_chunks,"vector_cero":vector_cero}
        ).fetchall()
        if not resultados:
            return []
        #converir a diccionario
        chunks = [
            {
                "contenido": r.contenido,
                "libro": r.libro
            }
            for r in resultados
        ]

        return chunks


    except Exception as e:
        print(f"❌ Error en buscar_similares: {e}")
        return []
    finally:
        session.close()