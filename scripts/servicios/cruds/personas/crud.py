from sqlalchemy import create_engine, text
from dotenv import load_dotenv
load_dotenv()
import os
import numpy as np
import jwt,datetime


# URL de conexión (la misma que en init_db.py)
DATABASE_URL = os.getenv("DATABASE_URL")
SECRET_KEY = "clave101"
ALGORITHM = "HS256"
# Crear engine
engine = create_engine(DATABASE_URL)

PREGUNTA_BASE = [
            ("Detalles", "País/Ciudad"),
            ("Detalles", "Fecha de nacimiento"),
            ("Detalles", "Profesíon u ocupación actual o pasada"),
            ("Personal", "¿Quién eres, de dónde vienes y qué experiencias marcaron tu vida?"),
            ("Personal", "¿Cuáles han sido los momentos más significativos de tu historia personal?"),
            ("Personal", "¿Qué valores y principios te guiaron a lo largo de tu vida?"),
            ("Personal", "¿Qué lecciones importantes aprendiste del camino recorrido?"),
            ("Personal", "¿Qué consejos te gustaría dejar a las futuras generaciones?"),
            ("Personal", "¿Cuál es tu mensaje personal desde tu experiencia como ser humano?"),
            ("Familiar", "¿Qué representa la familia para ti?"),
            ("Familiar", "Cuéntanos sobre tu familia de origen: tus padres, abuelos o antepasados."),
            ("Familiar", "¿Cómo formaste tu propio hogar o tu núcleo familiar?"),
            ("Familiar", "¿Qué enseñanzas o valores quisieras transmitir a tus hijos, nietos o parientes?"),
            ("Familiar", "¿Podrías compartir una historia o anécdota que refleje el espíritu de tu familia?"),
            ("Familiar", "¿Qué quisieras que tu familia recuerde de ti?"),
            ("Familiar", "¿Qué mensaje de amor o unión te gustaría dejar a las futuras generaciones de tu familia?"),
            ("Profesional", "Campo o especialidad profesional:"),
            ("Profesional", "¿Cómo empezó tu carrera y qué desafíos o logros recuerdas con más cariño?"),
            ("Profesional", "¿Qué proyectos o experiencias marcaron tu desarrollo profesional?"),
            ("Profesional", "¿Qué aprendizajes te dejó tu trabajo y tu trayectoria laboral?"),
            ("Profesional", "¿Qué consejos te gustaría compartir con las nuevas generaciones de profesionales?"),
            ("Profesional", "¿Cómo describirías lo que tu trabajo significó en tu vida?"),
            ("Educativa", "¿Qué papel ha tenido la educación en tu vida?"),
            ("Educativa", "¿Qué consejos darías a quienes recién inician su formación?"),
            ("Educativa", "¿Qué aprendizajes te dejó tu etapa como estudiante o maestro?"),
            ("Educativa", "¿Hay alguna frase o idea que te gustaría que los jóvenes recuerden?"),
            ("Educativa", "¿Qué mensaje dejarías a la comunidad educativa (maestros, colegas o alumnos)?"),
            ("Mensaje", "¿Cuál es el mensaje, pensamiento o reflexión que representa tu vida y tu legado?"),
            
        ]


def listar_personas():
    with engine.connect() as conn:
        result = conn.execute(text("SELECT id, nombre,apellidos, correo FROM persona"))
        rows = result.fetchall()
        print(rows)
        return [{"id": r.id, "nombre": r.nombre,"apellidos":r.apellidos, "correo": r.correo} for r in rows]

def obtener_persona(id: int):
    with engine.connect() as conn:
        result = conn.execute(
            text("""
                SELECT id, nombre, apellidos, correo
                FROM persona
                WHERE id = :id
                LIMIT 1
            """),
            {"id": id},
        )
        row = result.fetchone()
        if row:
            return {
                "id": row.id,
                "nombre": row.nombre,
                "apellidos": row.apellidos,
                "correo": row.correo,
            }
        else:
            return {"id":0,"nombre":"no encontrado"}

def eliminar(id: int):
    with engine.connect() as conn:
        result = conn.execute(text("DELETE FROM persona WHERE id = :id RETURNING id"), {"id": id})
        conn.commit()
        deleted = result.fetchone()
        if deleted:
            print(f"🗑️ Persona con ID {id} eliminada correctamente.")
        else:
            print(f"⚠️ No se encontró ninguna Archivo con ID {id}.")


def agregar(nombre, apellidos,fecha_nacimiento, correo, contrasena1, contrasena2):
    with engine.connect() as conn:
        query = text("""
            INSERT INTO persona (nombre, apellidos,fecha_nacimiento, correo, contrasena1, contrasena2)
            VALUES (:nombre, :apellidos,:fecha_nacimiento, :correo, :contrasena1, :contrasena2)
            RETURNING id;
        """)
        result = conn.execute(query,{
            "nombre": nombre,
            "apellidos": apellidos,
            "fecha_nacimiento": fecha_nacimiento,
            "correo": correo,
            "contrasena1": contrasena1,
            "contrasena2": contrasena2,
        })
        persona_id = result.scalar()
        vector_vacio = np.zeros(1536, dtype=np.float32).tolist()
        
        for faceta,pregunta in PREGUNTA_BASE:
            conn.execute(text("""
                INSERT INTO chunks (id_persona, faceta, pregunta, respuesta, embedding)
                VALUES (:id_persona, :faceta, :pregunta, '', :embedding);
            """),{"id_persona":persona_id, "faceta":faceta,"pregunta":pregunta, "embedding":vector_vacio})

        conn.commit()
        
        print(f"Persona agregada con id {persona_id} y {len(PREGUNTA_BASE)} preguntas base")
        return persona_id





def editar(id, nombre, apellidos,fecha_nacimiento, correo, contrasena1, contrasena2):
    with engine.connect() as conn:
        query = text("""
            UPDATE  persona
            SET nombre = :nombre,
                apellidos = :apellidos,
                fecha_nacimiento = :fecha_nacimiento,
                correo = :correo,
                contrasena1 = :contrasena1,
                contrasena2 = :contrasena2    
                WHERE id = :id
            RETURNING id;
        """)
        result = conn.execute(query,{
            "id":id,
            "nombre": nombre,
            "apellidos": apellidos,
            "fecha_nacimiento": fecha_nacimiento,
            "correo": correo,
            "contrasena1": contrasena1,
            "contrasena2": contrasena2,
        })
        conn.commit()
        updated = result.fetchone()
        if updated:
            print(f"Persona actualizada con id {id}")
        else:
            print(f"No se encontró ninguna persona con id {id}")

def acceso(correo,contrasena):

    with engine.connect() as conn:
        query = text("""
            SELECT id,contrasena1,correo FROM persona
            WHERE correo = :correo
            LIMIT 1;
        """)
        result = conn.execute(query,{"correo":correo})
        
        user = result.fetchone()
        if user:
                if user.contrasena1 == contrasena:
                    exp = datetime.datetime.utcnow() + datetime.timedelta(hours=1)
                    token = jwt.encode(
                        {"id": user.id, "correo": user.correo, "exp":exp},
                        SECRET_KEY,
                        algorithm=ALGORITHM
                    )
                    return {"id": user.id,"token":token, "message": "Ingresando"}
                else:
                    return {"id":0, "message":"Contraseña incorrecta"}
            
        else:
            return {"id": 0, "message":"No se encontro usuario"}
 
def login2(id,contrasena2):

    with engine.connect() as conn:
        query = text("""
            SELECT id,contrasena2 FROM persona
            WHERE id = :id
            LIMIT 1;
        """)
        result = conn.execute(query,{"id":id})
        
        user = result.fetchone()
        if user:
            if user.contrasena2 == contrasena2:
                return {"id": user.id, "message": "Contraseña correcta"}
            else:
                return {"id":0,"message":"Contraseña incorrecta"}
        else:
            return {"id": 0, "message":"No se encontro usuario"}
    




from datetime import date
if __name__ == "__main__":
     
    # agregar(
    # nombre="Jose",
    # apellidos=" Jaimes Soto",
    # fecha_nacimiento=None,
    # correo="jose@example.com",
    # contrasena1="12345",
    # contrasena2="12345"
    # )
    
    listar_personas()

    # editar(
    # id = 1,
    # nombre="Charles",
    # apellidos="Huamán Llacta",
    # fecha_nacimiento=date(2000, 5, 10),
    # correo="charles@example.com",
    # contrasena1="12345",
    # contrasena2="12345"
    # )

     
    #eliminar(1)
    