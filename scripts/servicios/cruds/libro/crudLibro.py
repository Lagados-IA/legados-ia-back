from pypdf import PdfReader
from io import BytesIO
from fastapi import UploadFile
from docx import Document
import os

async def extraer_texto(archivo: UploadFile) -> str:
    filename = archivo.filename.lower()

    contenido = await archivo.read()

    # --- PDF ---
    if filename.endswith(".pdf"):
        
        reader = PdfReader(BytesIO(contenido))
        texto_total = []
        for page in reader.pages:
            texto = page.extract_text()
            if texto:
                texto_total.append(texto)

        return "\n".join(texto_total)
    elif filename.endswith(".docx"):
        doc = Document(BytesIO(contenido))
        texto_total = []
        for para in doc.paragraphs:
            if para.text.strip():
                texto_total.append(para.text)
        return "\n".join(texto_total)
    else:
        raise ValueError("Formato de archivo no soportado. Usa PDF o DOCX.")
