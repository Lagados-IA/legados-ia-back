from fastapi import FastAPI, HTTPException,Form,File,Body,UploadFile
from pydantic import BaseModel
from datetime import datetime
from scripts.generar_respuesta import generar_respuesta_stream, generar_respuesta_audio
from scripts.servicios.cruds.personas.crud import listar_personas,obtener_persona,login2, acceso,agregar,editarPersona
from scripts.servicios.cruds.chunks.crud import editar, listar_preguntas_por_id, obtener_bio
from configurar_base_conocimiento.procesar_archivo import procesarArchivo
import uvicorn
import markdown2
from bs4 import BeautifulSoup
#puede ir en otro achivo ====
from typing import List, Literal, Optional
from fastapi.middleware.cors import CORSMiddleware
#puede ir en otro achivo ====
from dotenv import load_dotenv
import openai
import os
from io import BytesIO 
from pathlib import Path
import shutil
from fastapi.responses import JSONResponse

load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")
# Inicializar FastAPI
app = FastAPI(title="API RAG - Soporte Técnico")


BASE_DIR = os.path.dirname(os.path.abspath(__file__))  # desde app.py
CARPETA_INDEX = os.path.join(BASE_DIR, "index")

UPLOAD_DIR = Path("imagen")
UPLOAD_DIR.mkdir(exist_ok=True)

origins = [
    "http://localhost:3000",              
    "https://soporte2.intelectiasac.com", 
    "https://ipp.intelectiasac.com",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins, 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class Mensaje(BaseModel):
    rol: Literal["user", "bot"]
    contenido: str
# Modelo para recibir pregunta
class PreguntaEntrada(BaseModel):
    id: int
    nombre: str
    pregunta: str
    historial: List[Mensaje]
# Modelo de respuesta
class RespuestaSalida(BaseModel):
    respuesta: str












from fastapi.responses import StreamingResponse

@app.post("/consultar-stream")
def consultar_stream(pregunta_entrada: PreguntaEntrada):
    try:
        id = pregunta_entrada.id 
        nombre = pregunta_entrada.nombre
        pregunta = pregunta_entrada.pregunta
        historial = pregunta_entrada.historial

        generator = generar_respuesta_stream(id,nombre, pregunta, historial)
        
        return StreamingResponse(generator(), media_type="text/event-stream")
        
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))
    
import json
@app.post("/consultar-audio")
def consultar_audio(
        id: str = Form(...),
        nombre: str = Form(...),
        historial: str = Form(...),
        file: UploadFile = File(...)
    ):
    try:
        historial = json.loads(historial)
        audio_ia, texto_ia, texto_usuario = generar_respuesta_audio(id,nombre, file, historial)
        

        return {"audio_base64":audio_ia,"texto_ia": texto_ia, "texto_usuario": texto_usuario}
        
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))



@app.post("/imagen")
async def subir_imagen(file: UploadFile = File(...)):
    try:
        # Guardar el archivo con su nombre
        file_path = UPLOAD_DIR / file.filename
        with file_path.open("wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        # Retornar la URL pública para que tu frontend la use
        url_publica = f"/imagen/{file.filename}"
        return JSONResponse({"url": url_publica})
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error guardando imagen: {str(e)}")

# Servir las imágenes estáticas desde la carpeta
from fastapi.staticfiles import StaticFiles
app.mount("/imagen", StaticFiles(directory=UPLOAD_DIR), name="imagen")


    


@app.get("/listar_personas")
async def obtener_personas():
    personas = listar_personas()
    return personas

@app.get("/obtener_persona")
async def obtener_personas( id: int):
    personas = obtener_persona(id)
    
    return personas


@app.post("/crear_cuenta")
async def crear_persona(
    nombre: str = Form(...),
    apellidos: str = Form(...),
    fecha_nacimiento: datetime = Form(...),
    correo: str = Form(...),
    contrasena1: str = Form(...),
    contrasena2: str = Form(...),
    foto: str = Form(...),
    activacion: bool = Form(...),
):
    personaId = agregar(nombre,apellidos,fecha_nacimiento,correo,contrasena1,contrasena2,foto,activacion)
    return {"id":personaId}

@app.post("/editar_cuenta")
async def edit_persona(
    id: int = Form(...),
    nombre: str = Form(...),
    apellidos: str = Form(...),
    fecha_nacimiento: datetime = Form(...),
    correo: str = Form(...),
    contrasena1: str = Form(...),
    contrasena2: str = Form(...),
    foto: str = Form(...),
):
    editarPersona(id,nombre,apellidos,fecha_nacimiento,correo,contrasena1,contrasena2,foto)
    return {"status": "ok", "message": "Persona actualizada correctamente"}


@app.post("/acceso")
async def log(
    correo: str = Form(...),
    contrasena: str= Form(...),
    

):
    user = acceso(correo,contrasena)
    return user

@app.post("/login2")
async def log2(
    id:str = Form(...),
    contrasena2: str= Form(...),
):
    user = login2(id,contrasena2)
    return user



@app.get("/mostrar_preguntas")
async def mostrar_preguntas(
    id:str,
):
    return listar_preguntas_por_id(id)

@app.post("/subir-info")
async def subir_archivo(
    id_respuesta:str = Form(...),
    respuesta: str=Form(...)
):
    
    editar(id_respuesta,respuesta)
    return {"message": f"Respuesta {id_respuesta} actualizada correctamente ✅"}    

@app.get("/obtener_biografia")
async def obtener_personas( idPersona: int, textoPregunta:str ):
    biografia = obtener_bio(idPersona, textoPregunta)
    print(biografia)
    return biografia 





















# Ejecutar: uvicorn app:app --reload
if __name__ == "__main__":
    uvicorn.run("app:app", host="127.0.0.1", port=8000, reload=True)
