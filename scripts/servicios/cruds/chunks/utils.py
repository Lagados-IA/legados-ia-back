
import re

def limpiar_texto(texto: str) -> str:
    return re.sub(r'[\x00-\x08\x0B-\x0C\x0E-\x1F]','',texto)