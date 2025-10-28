import fitz
from PIL import Image
from concurrent.futures import ThreadPoolExecutor
import io
from google.cloud import vision_v1 as vision
import zipfile
from docx import Document
import os
from dotenv import load_dotenv

load_dotenv()
json_str = os.getenv("GOOGLE_JSON")
if json_str:
    with open("credenciales.json","w") as f:
        f.write(json_str)
    os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "credenciales.json"
else:
    raise EnvironmentError("❌ Falta la variable de entorno GOGLE_D_JSON")


client = vision.ImageAnnotatorClient()
contador_ocr = {"total":0}
def ocr_imagen_pil(img_pil):
    try:
        img_byte_arr = io.BytesIO()
        img_pil.save(img_byte_arr, format='PNG')
        content = img_byte_arr.getvalue()
        image = vision.Image(content = content)
        response = client.document_text_detection(image= image)
        if response.error.message:
            print(f"Error OCR: {response.error.message}")
            return ""
        else:
            contador_ocr("total") +1
            return response.full_text_annotation.text.strip()
    except Exception as e:
        print(f"Error procesando OCR: {e}")
        return ""

def extraer_texto_docx(contenido: bytes) -> list[dict]:
    paginas, imagenes_pagina = [], {}
    pagina_actual = 1
    texto_pagina = []

    docx_stream = io.BytesIO(contenido)
    doc = Document(docx_stream)

    for para in doc.paragraphs:
        for run in para.runs:
            if run.text.strip():
                texto_pagina.append(run.text.strip())

            # salto pagina
            if "lastRenderedPageBreak" in run._element.xml or "w:br w:type=\"page\"" in run._element.xml:
                paginas.append({"pagina": pagina_actual, "texto": "\n".join(texto_pagina).strip()})
                pagina_actual += 1
                texto_pagina = []

    if texto_pagina:
        paginas.append({"pagina": pagina_actual, "texto": "\n".join(texto_pagina).strip()})

    #extraer img
    imagenes_pagina = {i["pagina"]: [] for i in paginas}
    with zipfile.ZipFile(io.BytesIO(contenido)) as zip_ref:
        for file in zip_ref.namelist():
            if file.startswith("word/media/") and file.lower().endswith((".png", ".jpg", ".jpeg")):
                data = zip_ref.read(file)
                img_pil = Image.open(io.BytesIO(data)).convert("RGB")
                if img_pil.width < 120 or img_pil.height < 120:
                    continue
                if img_pil.width > 1500:
                    new_height = int(img_pil.height * 1500 / img_pil.width)
                    img_pil = img_pil.resize((1500, new_height))
                # Por simplicidad asignamos al final de la última página
                imagenes_pagina[pagina_actual].append(img_pil)

    with ThreadPoolExecutor(max_workers=4) as executor:
        futures = {num: executor.submit(lambda imgs=imgs: "\n".join([ocr_imagen_pil(im) for im in imgs]))
            for num, imgs in imagenes_pagina.items() if imgs}

        for pagina in paginas:
            num = pagina["pagina"]
            if num in futures:
                try:
                    texto_ocr = futures[num].result().strip()
                    if texto_ocr:
                        pagina["texto"] = (pagina["texto"] + "\n" + texto_ocr).strip()
                except Exception as e:
                    print(f"Error OCR en pag {num}: {e}")

    return paginas



def extraer_texto_pdf(contenido:bytes) -> list[dict]:
    paginas = []
    doc = fitz.open("pdf", contenido)

    with ThreadPoolExecutor(max_workers=4) as executor:
        futures = []

        for pagina in doc:
            numero_pag = pagina.number +1
            texto_pag = pagina.get_text().strip()

            imagenes_pil = []
            for img_index, img in enumerate(pagina.get_images(full = True)):
                try:
                    xref = img[0]
                    base_image = doc.extract_image(xref)
                    image_bytes = base_image["image"]

                    img_pil = Image.open(io.BytesIO(image_bytes)).convert("RGB")
                    if img_pil.width < 120 or img_pil.height < 120:
                        continue
                    if img_pil.width > 1500:
                        new_height = int(img_pil.height * 1500 / img_pil.width)
                        img_pil = img_pil.resize((1500, new_height))
                    imagenes_pil.append(img_pil)
                except Exception as e:
                    print(f"No se pudo procesar imagen en pág {numero_pag}: {e}")
            if imagenes_pil:
                futures.append((numero_pag,texto_pag, executor.submit(
                    lambda imgs= imagenes_pil: "\n".join([ocr_imagen_pil(im) for im in imgs])
                )))
            else:
                paginas.append({"pagina": numero_pag, "texto": texto_pag})
        for numero_pag, texto_pag, future in futures:
            try:
                texto_ocr = future.result().strip()
                texto_final = (texto_pag + "\n" + texto_ocr).strip() if texto_ocr else texto_pag
                paginas.append({"pagina":numero_pag, "texto": texto_final})
            except Exception as e:
                print(f"Error en pag: {numero_pag}: {e}")
                paginas.append({"pagina": {numero_pag}, "texto": {texto_pag}})
    return paginas