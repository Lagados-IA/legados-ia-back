import faiss
import os
import numpy as np
import os

CARPETA_INDEX = "index"

def generar_vectores_promedio():
    # recorrer dentro de carpeta INDEX, solo si termina con .index
    archivos = [f for f in os.listdir(CARPETA_INDEX) if f.endswith(".index")]
    # para cada archivo se realizan estas funciones
    for archivo in archivos:
        # borrar extencion .index
        nombre_base = archivo.replace(".index", "")
        #obtener ruta
        ruta_index = os.path.join(CARPETA_INDEX, archivo)
        # nuevo archivo con nuevo nombre
        ruta_salida = os.path.join(CARPETA_INDEX, f"{nombre_base}_vector.npy")

        print(f"📦 Procesando: {archivo}")

        # Leer el índice / desearializa los datos binarios
        index = faiss.read_index(ruta_index)
        # Reconstruir todos los vectores / 
        vectores = index.reconstruct_n(0, index.ntotal)

        # Calcular promedio
        vector_promedio = np.mean(vectores, axis=0)

        # Guardar .npy
        np.save(ruta_salida, vector_promedio)
        print(f"   💾 Guardado: {ruta_salida}")

    print("\n✅ Todos los vectores promedio generados.")

if __name__ == "__main__":
    generar_vectores_promedio()
