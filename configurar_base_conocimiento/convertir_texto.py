import os
import unicodedata
from configurar_base_conocimiento.ocr import extraer_texto_docx, extraer_texto_pdf

def normalizar_nombre_archivo(nombre):
    nombre = unicodedata.normalize('NFKD',nombre).encode('ASCII','ignore').decode('utf-8')
    
    nombre = nombre.replace(" ","-")
    nombre = ''.join(c for c in nombre if c.isalnum() or c in ['-','_'])
    return nombre.lower()


def archivo_a_txt(contenido, nombre_archivo):
    archivo_lower = nombre_archivo.lower() 
    nombre_base, ext = os.path.splitext(archivo_lower)
    nombre_base = normalizar_nombre_archivo(nombre_base)
    texto=""
    if ext == '.pdf':
        paginas = extraer_texto_pdf(contenido)
        
    elif ext == '.docx':
        paginas = extraer_texto_docx(contenido)
    elif ext == '.txt':
        texto = contenido.decode("utf-8", errors="replace")
        paginas = [{"pagina": 1, "texto": texto}]
    else:
        return None
    return paginas,nombre_base
