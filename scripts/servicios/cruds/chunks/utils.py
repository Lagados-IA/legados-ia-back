
import re
from scripts.editar_variables import CHUNK_LIBRO,OVERLAP
def limpiar_texto(texto: str) -> str:
    return re.sub(r'[\x00-\x08\x0B-\x0C\x0E-\x1F]','',texto)

def dividir_en_chunks(texto: str, max_palabras: int = CHUNK_LIBRO, overlap: int = OVERLAP) -> list[str]:
    texto = re.sub(r"\s+", " ", texto).strip()

    palabras = texto.split(" ")
    chunks = []

    inicio = 0
    while inicio < len(palabras):
        fin = inicio + max_palabras
        chunk = palabras[inicio:fin]
        chunks.append(" ".join(chunk))
        inicio = fin - overlap

    return chunks
