import os

CARPETA_INDEX = "index"

# Crear carpeta si no existe
if not os.path.exists(CARPETA_INDEX):
    os.makedirs(CARPETA_INDEX)

def elegir_todos_los_agentes():
    agentes = []
    for archivo in os.listdir(CARPETA_INDEX):
        if archivo.endswith("_vector.npy"):
            nombre_base = archivo.replace("_vector.npy", "")
            agentes.append({
                "nombre": nombre_base,
                "ruta_index": os.path.join(CARPETA_INDEX, f"{nombre_base}.index"),
                "ruta_json": os.path.join(CARPETA_INDEX, f"{nombre_base}.json")
            })
    return agentes
