import numpy as np
from scripts.utilitarios.embedding import generar_embedding 

from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

from configurar_base_conocimiento.bd.init_db import Correccion 
# Ruta donde guardamos las correcciones

DATABASE_URL = "postgresql://ingenieros_user:RPN3vIieAiYqSfWe85RoiY8z8IMNj4nK@dpg-d2nhqb95pdvs73bvh8f0-a.oregon-postgres.render.com/ingenieros"
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)



# guarda los datos correctos en un json para ir aprendiendo
def guardar_correccion(pregunta: str, respuesta: str):
    session = SessionLocal()
    
    try:
        embedding = generar_embedding(pregunta)

        embedding = embedding.tolist() if isinstance(embedding, np.ndarray) else embedding
        nueva = Correccion(
            pregunta=pregunta,
            respuesta=respuesta,
            embedding=embedding
        )
        session.add(nueva)
        session.commit()
        print(f"Corrección guardada en BD: {pregunta} → {respuesta}")
    except Exception as e:
        session.rollback()
        print(f"Error al guradar entrenamiento: -> {e}")


def buscar_correccion(pregunta: str, umbral: float = 0.60):
    
    session = SessionLocal()
    try:
        
        emb_pregunta = generar_embedding(pregunta)
        if isinstance(emb_pregunta, np.ndarray):
            emb_pregunta = emb_pregunta.tolist()

        query = text("""
            SELECT id, respuesta,
                   1 - (embedding <-> (:pregunta)::vector) AS similitud
            FROM correcciones
            ORDER BY similitud DESC
            LIMIT 1
        """)
        resultado = session.execute(query,{"pregunta": emb_pregunta}).fetchone()
        if resultado and resultado.similitud >= umbral:
            return resultado.respuesta
        return None

    except Exception as e:
        print(f"Error al buscar CORRECION ENTRENAMINETO {e}")
        return None

if __name__ == "__main__":
    #guardar_correccion("en que se enfoca el IPP, que competencias trasnversales o tecnicas?", "El IPP asegura que los ingenieros desarrollen competencias transversales como ética, valores, liderazgo, innovación, sostenibilidad, comunicación, trabajo en equipo y entre otros")
    print(buscar_correccion("en que se enfoca el IPP, que competencias trasnversales o tecnicas"))