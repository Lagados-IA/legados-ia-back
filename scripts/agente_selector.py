import os
import numpy as np
from scripts.utilitarios.embedding import generar_embedding  # Usa tu función existente
from configurar_base_conocimiento.bd.init_db import Archivo
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

# Config DB
VECTORES_CACHE = None
DATABASE_URL = "postgresql://ingenieros_user:RPN3vIieAiYqSfWe85RoiY8z8IMNj4nK@dpg-d2nhqb95pdvs73bvh8f0-a.oregon-postgres.render.com/ingenieros"
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)

import numpy as np



# def elegir_mejor_json_por_embedding(pregunta: str, top_k: int = 2):
#     session = SessionLocal()
#     try:
#         t0 = time.time()
#         vector_pregunta = generar_embedding(pregunta)
#         t1 = time.time()
#         print("⏱ Generar embedding:", t1 - t0)

#         # Asegurar numpy array para la pregunta
#         if isinstance(vector_pregunta, list):
#             vector_pregunta = np.array(vector_pregunta, dtype=float)
#         elif isinstance(vector_pregunta, np.ndarray):
#             vector_pregunta = vector_pregunta.astype(float)

#         print("🔍 Buscando agente más cercano...")

#         candidados = cargar_vectores_promedio(session)
#         distancias = []

#         for doc in candidados:
#             raw_vector = doc["vector"]

#             # --- Conversión robusta ---
#             vector_doc = None
#             if isinstance(raw_vector, list):
#                 vector_doc = np.array(raw_vector, dtype=float)
#             elif isinstance(raw_vector, np.ndarray):
#                 vector_doc = raw_vector.astype(float)
#             elif isinstance(raw_vector, str):
#                 try:
#                     # 1) Intentar como JSON válido
#                     vector_doc = np.array(json.loads(raw_vector), dtype=float)
#                 except Exception:
#                     try:
#                         # 2) Intentar como literal de Python
#                         vector_doc = np.array(ast.literal_eval(raw_vector), dtype=float)
#                     except Exception:
#                         try:
#                             # 3) Última opción: limpiar corchetes y parsear como CSV
#                             valores = [float(x.strip()) for x in raw_vector.strip("[]").split(",")]
#                             vector_doc = np.array(valores, dtype=float)
#                         except Exception as inner_e:
#                             print(f"⚠ No se pudo convertir vector de doc {doc['id']}: {inner_e}")
#                             continue
#             else:
#                 print(f"⚠ Tipo no soportado en doc {doc['id']}: {type(raw_vector)}")
#                 continue
#             # --------------------------

#             sim = cosine_similarity([vector_pregunta], [vector_doc])[0][0]
#             distancias.append({
#                 "id": doc["id"],
#                 "nombre": doc["nombre"],
#                 "distancia": 1 - sim
#             })

#         distancias.sort(key=lambda x: x["distancia"])
#         return distancias[:top_k]

#     except Exception as e:
#         print(f"❌ Error en búsqueda: {e}")
#         return []

def cargar_vectores_promedio(session):
    global VECTORES_CACHE
    if VECTORES_CACHE is None:  # solo cargamos si está vacío
        resultados = session.execute(text("""
            SELECT id, nombre_archivo, vector_promedio
            FROM archivos
            WHERE vector_promedio IS NOT NULL
        """)).fetchall()
        
        VECTORES_CACHE = []
        for r in resultados:
            vec = np.array(r.vector_promedio, dtype=float)
            VECTORES_CACHE.append({
                "id": r.id,
                "nombre": r.nombre_archivo,
                "vector": vec
            })
    return VECTORES_CACHE


def elegir_mejor_json_por_embedding(pregunta: str, top_k: int = 2):

    session  = SessionLocal()
    try:
        vector_pregunta = generar_embedding(pregunta)
        if isinstance(vector_pregunta, np.ndarray):
            vector_pregunta = vector_pregunta.tolist()

        print("🔍 Buscando agente más cercano...")
        session.execute(text("SET enable_seqscan = OFF;"))
        session.execute(text("SET hnsw.ef_search = 50;"))

        query = text(f"""
            SELECT id, nombre_archivo, vector_promedio <-> (:pregunta)::vector AS distancia
            FROM archivos_resumen
            WHERE vector_promedio IS NOT NULL
            ORDER BY distancia ASC
            LIMIT {top_k}
        """)
        resultados = session.execute(
            query,
            {"pregunta":vector_pregunta}
        ).fetchall()

    
        candidatos = [
            {"id": r.id, "nombre": r.nombre_archivo, "distancia":r.distancia}
            for r in resultados
        ]
        if candidatos:
            print(f"✅ Agente elegido:", [a["nombre"] for a in candidatos])
        else:
            print("⚠ No se encontró un agente apropiado.")
        return candidatos
        
    except Exception as e:
        print(f"❌ Error en búsqueda: {e}")
        return []
