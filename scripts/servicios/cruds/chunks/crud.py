import os
from sqlalchemy import create_engine,text
from dotenv import load_dotenv
from .utils import limpiar_texto
import numpy as np

from scripts.utilitarios.embedding.embedding import generar_embedding


load_dotenv()

DATABASE_URL=os.getenv("DATABASE_URL")
engine = create_engine(DATABASE_URL)





def listar_preguntas_por_id(id_persona):
    with engine.connect() as conn:
        query = text("""
            SELECT id, faceta, pregunta, respuesta
            FROM chunks
            WHERE id_persona = :id_persona
        """)
        result = conn.execute(query, {"id_persona": id_persona})
        rows = result.mappings().all() 
        print( [dict(r) for r in rows])
        return [dict(r) for r in rows]

    

def editar(id,respuesta):
    chunk_limpio = limpiar_texto(respuesta)
    embedding = generar_embedding(chunk_limpio)
    emb = np.array(embedding,dtype=np.float32)
    with engine.begin() as conn:
        query = text("""
            UPDATE chunks
            SET respuesta = :respuesta,
                embedding = :embedding
                WHERE id = :id
            RETURNING id;
        """)
        result = conn.execute(query,{
            "id": id,
            "respuesta": respuesta,
            "embedding": emb.tolist(),
        })
        updated = result.fetchone()
        if updated:
            print(f"actualizado con id {id}")
        else:
            print(f"No se encontró ninguna registro con id {id}")  


    
def obtener_bio(idPersona: int, textoPregunta: str):
    with engine.connect() as conn:
        result = conn.execute(
            text("""
                SELECT id, faceta, pregunta, respuesta
                FROM chunks
                WHERE id_persona = :id_persona
                AND pregunta ILIKE :pregunta
            """),
            {"id_persona": idPersona, "pregunta": f"%{textoPregunta}%"},
        )
        rows = result.mappings().all()
        return [dict(r) for r in rows]
        




if __name__ == "__main__":
    
    #editar(1,"Charles huaman llaccta")
    listar_preguntas_por_id(5)