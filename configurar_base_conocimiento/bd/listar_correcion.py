from sqlalchemy import create_engine, text

# URL de conexión (la misma que en init_db.py)
DATABASE_URL = "postgresql://ingenieros_user:RPN3vIieAiYqSfWe85RoiY8z8IMNj4nK@dpg-d2nhqb95pdvs73bvh8f0-a.oregon-postgres.render.com/ingenieros"

# Crear engine
engine = create_engine(DATABASE_URL)

def listar_correcciones():
    with engine.connect() as conn:
        result = conn.execute(text("SELECT id, pregunta, respuesta FROM correcciones"))
        rows = result.fetchall()

        if not rows:
            print("⚠️ La tabla 'correcciones' está vacía.")
        else:
            print(f"✅ Se encontraron {len(rows)} correcciones:\n")
            for row in rows:
                print(f"ID: {row.id}")
                print(f"Pregunta: {row.pregunta}")
                print(f"Respuesta: {row.respuesta}")
                print("-" * 50)

def eliminar_correccion(id_correccion: int):
    with engine.connect() as conn:
        result = conn.execute(text("DELETE FROM correcciones WHERE id = :id RETURNING id"), {"id": id_correccion})
        conn.commit()
        deleted = result.fetchone()
        if deleted:
            print(f"🗑️ Corrección con ID {id_correccion} eliminada correctamente.")
        else:
            print(f"⚠️ No se encontró ninguna corrección con ID {id_correccion}.")

#if __name__ == "__main__":
    ##listar_correcciones()
    #eliminar_correccion(44)