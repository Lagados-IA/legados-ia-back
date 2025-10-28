# check_pgvector.py
from sqlalchemy import create_engine, text

DATABASE_URL = "postgresql://ingenieros_user:RPN3vIieAiYqSfWe85RoiY8z8IMNj4nK@dpg-d2nhqb95pdvs73bvh8f0-a.oregon-postgres.render.com/ingenieros"

engine = create_engine(DATABASE_URL)

def check_pgvector():
    with engine.connect() as conn:
        result = conn.execute(
            text("SELECT * FROM pg_extension WHERE extname = 'vector';")
        )
        row = result.fetchone()
        if row:
            print("✅ pgvector está instalado:", row)
        else:
            print("❌ pgvector NO está instalado en esta base de datos.")

if __name__ == "__main__":
    check_pgvector()
