from fastapi import FastAPI, HTTPException,Form,File,Body,UploadFile
from pydantic import BaseModel
from datetime import datetime
from scripts.consulta_rag import generar_respuesta_stream,generar_respuesta
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
import base64

load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")
# Inicializar FastAPI
app = FastAPI(title="API RAG - Soporte Técnico")

import requests 

BASE_DIR = os.path.dirname(os.path.abspath(__file__))  # desde app.py
CARPETA_INDEX = os.path.join(BASE_DIR, "index")



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
    rol: Literal["usuario", "bot"]
    contenido: str
# Modelo para recibir pregunta
class PreguntaEntrada(BaseModel):
    pregunta: str
    historial: List[Mensaje]
# Modelo de respuesta
class RespuestaSalida(BaseModel):
    respuesta: str
    tokens: int
    modelo: str
    timestamp: str





@app.post("/consultar", response_model=RespuestaSalida)
def consultar(pregunta_entrada: PreguntaEntrada):
    try:
        
        pregunta = pregunta_entrada.pregunta
        historial = pregunta_entrada.historial
        # pasamos los datos a la funcion generar respuesta
        respuesta_texto, modelo_usado, tokens_utilizados = generar_respuesta(pregunta,historial)
        print(respuesta_texto)

        # Armar respuesta completa
        return RespuestaSalida(
            respuesta=respuesta_texto,  
            tokens=tokens_utilizados,
            modelo = modelo_usado,
            timestamp=datetime.now().isoformat(),
        )


    except Exception as e:
        import traceback
        print("Error en /consultar:",e)
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))
    









from fastapi.responses import StreamingResponse

@app.post("/consultar-stream")
def consultar_stream(pregunta_entrada: PreguntaEntrada):
    try:
        pregunta = pregunta_entrada.pregunta
        historial = pregunta_entrada.historial

        generator = generar_respuesta_stream(pregunta, historial)
        
        return StreamingResponse(generator(), media_type="text/event-stream")
        
    except Exception as e:
        import traceback
        print("Error en /consultar-stream:", e)
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))




@app.post("/subir-archivo")
async def subir_archivo(
    clave_front: str= Form(...),
    archivo: UploadFile = File(...)
):
    clave = "jorgecuadros"
    if clave_front  != clave or clave == "":
        raise HTTPException(status_code=401, detail="Clave incorrecta")
    try:
        contenido = await archivo.read()
        nombre_archivo = archivo.filename
        procesarArchivo(contenido, nombre_archivo)
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))
   

# Ejecutar: uvicorn app:app --reload
if __name__ == "__main__":
    uvicorn.run("app:app", host="127.0.0.1", port=8000, reload=True)
