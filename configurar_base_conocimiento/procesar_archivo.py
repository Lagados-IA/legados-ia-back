from configurar_base_conocimiento.convertir_texto import archivo_a_txt
from configurar_base_conocimiento.indexacion import indexar

def procesarArchivo(contenido: bytes, nombre_archivo:str):
    paginas, nuevo_nombre = archivo_a_txt(contenido, nombre_archivo)

    indexar(nuevo_nombre, paginas)

    