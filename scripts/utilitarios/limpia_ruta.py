import os

def limpiar_ruta(ruta: str) -> str:
    # Obtener el nombre del archivo sin extensión
    nombre = os.path.splitext(os.path.basename(ruta))[0]
    # Reemplazar guiones y guiones bajos por espacios
    nombre_limpio = nombre.replace("-", " ").replace("_", " ")
    return nombre_limpio
