import os
from sqlalchemy import create_engine,text
from dotenv import load_dotenv
from .utils import limpiar_texto, dividir_en_chunks
import numpy as np
import uuid


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

def subirLibro(id_persona,nombreLibro, contenido):
    """
    contenido: texto completo del libro
    """
    chunks = dividir_en_chunks(contenido )
    libro_uuid = str(uuid.uuid4())

    with engine.begin() as conn:

        conn.execute(
            text("""
                INSERT INTO libros (id_persona, libro, uuid)
                VALUES (:id_persona, :libro, :uuid)
            """),
            {
                "id_persona":id_persona,
                "libro": nombreLibro,
                "uuid": libro_uuid
            }
        )
        query = text("""
            INSERT INTO document_chunks
                (id_persona, libro,libro_uuid, contenido, embedding)
            VALUES
                (:id_persona, :libro, :libro_uuid, :contenido, :embedding)
        """)
        for texto in chunks:
            chunk_limpio = limpiar_texto(texto)
            embedding = generar_embedding(chunk_limpio)

            emb = np.array(embedding, dtype=np.float32)

            
            conn.execute(
                query,
                {
                    "id_persona": id_persona,
                    "libro": nombreLibro,
                    "libro_uuid": libro_uuid,
                    "contenido": chunk_limpio,
                    "embedding": emb.tolist(),
                }
            )



def listar_libro():
    with engine.begin() as conn:
        result = conn.execute(
            text("""
                SELECT id, id_persona, libro, uuid
                FROM libros
            """)
        ).mappings().all()
    print(result)

    return result

# Eliminar
def eliminar_libro(uuid: str):
    with engine.begin() as conn:

        # 1️⃣ Verificar existencia
        libro = conn.execute(
            text("""
                SELECT id FROM libros WHERE uuid = :uuid
            """),
            {"uuid": uuid}
        ).fetchone()

        if not libro:
            raise ValueError("Libro no encontrado")

        # 2️⃣ Eliminar chunks primero
        result_chunks = conn.execute(
            text("""
                DELETE FROM document_chunks
                WHERE libro_uuid = :uuid
            """),
            {"uuid": uuid}
        )

        # 3️⃣ Eliminar libro
        conn.execute(
            text("""
                DELETE FROM libros
                WHERE uuid = :uuid
            """),
            {"uuid": uuid}
        )

    return {
        "message": "Libro eliminado correctamente",
        "chunks_eliminados": result_chunks.rowcount
    }




    

    
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
    #eliminar_libro("0791c8fb-9bb3-40cc-852e-90679ee03dd9")
    listar_libro()
    
    #editar(1,"Charles huaman llaccta")
    #listar_preguntas_por_id(5)