import os

from dotenv import load_dotenv
from sqlalchemy import create_engine, Column, Integer, Text, ForeignKey,Date,Boolean,String,text
from sqlalchemy.orm import declarative_base, relationship
from pgvector.sqlalchemy import Vector 

load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL")
engine = create_engine(DATABASE_URL)
Base = declarative_base()

class Persona(Base):
    __tablename__ = "persona"

    id = Column(Integer, primary_key=True, autoincrement=True)
    nombre = Column(Text )
    apellidos = Column(Text)
    fecha_nacimiento = Column(Date)
    correo = Column(Text)
    contrasena1 = Column(Text)
    contrasena2 = Column(Text)
    foto = Column(Text)
    activacion = Column(Boolean, default=False)


    chunks = relationship("Chunks", back_populates="persona", cascade="all, delete-orphan")
    document_chunks = relationship("DocumentChunks",back_populates="persona",cascade="all, delete-orphan")




class Chunks(Base):
    __tablename__ = "chunks"
    id = Column(Integer, primary_key=True, autoincrement=True)
    id_persona = Column(Integer, ForeignKey("persona.id", ondelete="CASCADE"))
    faceta = Column(Text)
    pregunta = Column(Text)
    respuesta = Column(Text)
    embedding = Column(Vector(1536)) 

    # Relaciones
    persona = relationship("Persona", back_populates="chunks")



class DocumentChunks(Base):
    __tablename__ = "document_chunks"
    id = Column(Integer, primary_key=True, autoincrement=True)
    id_persona = Column(Integer,ForeignKey("persona.id", ondelete="CASCADE"),nullable=False)
    libro = Column(Text, nullable=False)
    libro_uuid = Column(String(36), nullable=False)
    contenido = Column(Text, nullable=False)
    embedding = Column(Vector(1536), nullable=False)
    persona = relationship("Persona", back_populates="document_chunks")

class Libros(Base):
    __tablename__ = "libros"
    id = Column(Integer, primary_key=True, autoincrement=True)
    id_persona = Column(Integer, nullable=False)
    libro = Column(Text,nullable=False)
    uuid = Column(String(36), unique=True, nullable=False)
    






def init_db():
    # 1. Crear extensión pgvector antes que cualquier tabla
    with engine.connect() as conn:
         conn.execute(text("CREATE EXTENSION IF NOT EXISTS vector;"))
         conn.commit()
    # 2. Ahora crear las tablas
    Base.metadata.create_all(bind=engine)

     # 3. Crear índice vectorial
    with engine.connect() as conn:
        conn.execute(text("""
            CREATE INDEX IF NOT EXISTS document_chunks_embedding_ivfflat
            ON document_chunks
            USING ivfflat (embedding vector_cosine_ops)
            WITH (lists = 50);
        """))
        conn.execute(text("ANALYZE document_chunks;"))
        conn.commit()

    print("✅ Tablas creadas correctamente con pgvector.")


if __name__ == "__main__":
    init_db()
