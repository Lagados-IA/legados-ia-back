import os
import numpy as np
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def generar_embedding(texto: str) -> np.ndarray:
    response = client.embeddings.create(
        model="text-embedding-3-small",
        input=texto
    )
    return np.array(response.data[0].embedding, dtype="float32")


