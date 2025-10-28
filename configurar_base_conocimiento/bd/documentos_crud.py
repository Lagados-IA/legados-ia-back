from sqlalchemy import create_engine, text

# URL de conexión (la misma que en init_db.py)
DATABASE_URL = "postgresql://ingenieros_user:RPN3vIieAiYqSfWe85RoiY8z8IMNj4nK@dpg-d2nhqb95pdvs73bvh8f0-a.oregon-postgres.render.com/ingenieros"

# Crear engine
engine = create_engine(DATABASE_URL)

def listar_archivos():
    with engine.connect() as conn:
        result = conn.execute(text("SELECT id, nombre_archivo FROM archivos"))
        rows = result.fetchall()

        if not rows:
            print("⚠️ La tabla 'archivos' está vacía.")
        else:
            print(f"✅ Se encontraron {len(rows)} archivos:\n")
            for row in rows:
                print(f"ID: {row.id}")
                print(f"Pregunta: {row.nombre_archivo}")
                print("-" * 50)

def eliminar(id: int):
    with engine.connect() as conn:
        result = conn.execute(text("DELETE FROM archivos WHERE id = :id RETURNING id"), {"id": id})
        conn.commit()
        deleted = result.fetchone()
        if deleted:
            print(f"🗑️ Archivo con ID {id} eliminada correctamente.")
        else:
            print(f"⚠️ No se encontró ninguna Archivo con ID {id}.")

#if __name__ == "__main__":
    #listar_archivos()
     
    #eliminar(83)