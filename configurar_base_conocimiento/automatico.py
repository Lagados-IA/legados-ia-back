import os

from configurar_base_conocimiento.procesar_archivo import procesarArchivo

# Carpeta donde están los archivos
CARPETA_ARCHIVOS = "data"

for nombre_archivo in os.listdir(CARPETA_ARCHIVOS):
    ruta_archivo = os.path.join(CARPETA_ARCHIVOS, nombre_archivo)
    
    
    if os.path.isfile(ruta_archivo):
        with open(ruta_archivo, "rb") as f:
            contenido = f.read()
        procesarArchivo(contenido, nombre_archivo)
