import os
from scripts.utilitarios.limpia_ruta import limpiar_ruta
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

DATABASE_URL = "postgresql://ingenieros_user:RPN3vIieAiYqSfWe85RoiY8z8IMNj4nK@dpg-d2nhqb95pdvs73bvh8f0-a.oregon-postgres.render.com/ingenieros"
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)

def obtener_documentos():
    session = SessionLocal()
    try:
        query = text("SELECT id, nombre_archivo FROM archivos_resumen ORDER BY id ASC")
        resultados = session.execute(query).fetchall()
        documentos = [f"{r.nombre_archivo}" for r in resultados]

        return documentos
    except Exception as e:
        print(f"❌ Error al obtener documentos: {e}")
        return []
    
