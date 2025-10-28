# drop_tables.py
from sqlalchemy import create_engine, text

DATABASE_URL = "postgresql://ingenieros_user:RPN3vIieAiYqSfWe85RoiY8z8IMNj4nK@dpg-d2nhqb95pdvs73bvh8f0-a.oregon-postgres.render.com/ingenieros"

engine = create_engine(DATABASE_URL)

def drop_tables():
    with engine.connect() as conn:
        conn.execute(text("DROP TABLE IF EXISTS archivos_resumen CASCADE; DROP TABLE IF EXISTS documentos_embedding_resumen CASCADE; "))
        conn.commit()
        print("🗑️ Tablas eliminada correctamente.")

if __name__ == "__main__":
    drop_tables()
