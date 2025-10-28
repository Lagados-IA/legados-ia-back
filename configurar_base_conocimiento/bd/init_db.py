# init_db.py
import os
from sqlalchemy import create_engine, Column, Integer, Text, ForeignKey
from sqlalchemy.orm import declarative_base, relationship
from sqlalchemy import text
from pgvector.sqlalchemy import Vector 

DATABASE_URL = "postgresql://ingenieros_user:RPN3vIieAiYqSfWe85RoiY8z8IMNj4nK@dpg-d2nhqb95pdvs73bvh8f0-a.oregon-postgres.render.com/ingenieros"

engine = create_engine(DATABASE_URL)
Base = declarative_base()

#Tabla: archivos


class Archivo(Base):
    __tablename__ = "archivos"
    id = Column(Integer, primary_key=True, autoincrement=True)
    nombre_archivo = Column(Text, nullable=False)
    vector_promedio = Column(Vector(1536))
    # Relación con documentos_embedding
    documentos = relationship("DocumentoEmbedding", back_populates="archivo", cascade="all, delete-orphan")


# Tabla: documentos_embedding
class DocumentoEmbedding(Base):
    __tablename__ = "documentos_embedding"
    id = Column(Integer, primary_key=True, autoincrement=True)
    id_archivo = Column(Integer, ForeignKey("archivos.id", ondelete="CASCADE"), nullable=False)
    texto = Column(Text, nullable=False)
    embedding = Column(Vector(1536))  # ajusta al tamaño del embedding de tu modelo
    num_pag = Column(Integer)
    # Relación inversa con archivos
    archivo = relationship("Archivo", back_populates="documentos")

class Correccion(Base):
    __tablename__ = "correcciones"

    id = Column(Integer, primary_key=True, autoincrement=True)
    pregunta = Column(Text, nullable=False)
    respuesta = Column(Text, nullable=False)
    embedding = Column(Vector(1536))  # Ajusta tamaño según el embedding

class ArchivoResumen(Base):
    __tablename__ = "archivos_resumen"
    id = Column(Integer, primary_key=True, autoincrement=True)
    nombre_archivo = Column(Text, nullable=False)
    vector_promedio = Column(Vector(1536))
    # Relación con documentos_embedding
    documentos = relationship("DocumentoEmbeddingResumen", back_populates="archivos_resumen", cascade="all, delete-orphan")


# Tabla: documentos_embedding
class DocumentoEmbeddingResumen(Base):
    __tablename__ = "documentos_embedding_resumen"
    id = Column(Integer, primary_key=True, autoincrement=True)
    id_archivo = Column(Integer, ForeignKey("archivos_resumen.id", ondelete="CASCADE"), nullable=False)
    texto = Column(Text, nullable=False)
    embedding = Column(Vector(1536))  # ajusta al tamaño del embedding de tu modelo
    num_pag = Column(Integer)
    # Relación inversa con archivos
    archivos_resumen = relationship("ArchivoResumen", back_populates="documentos")


def init_db():
    # 1. Crear extensión pgvector antes que cualquier tabla
    with engine.connect() as conn:
         conn.execute(text("CREATE EXTENSION IF NOT EXISTS vector;"))
         conn.commit()
    # # 2. Ahora sí, crear las tablas
    Base.metadata.create_all(bind=engine)

    with engine.connect() as conn:
        #índice principal para búsquedas vectoriales
        
        conn.execute(text("""
        CREATE INDEX IF NOT EXISTS documentos_embedding_hnsw_idx
            ON documentos_embedding
            USING hnsw (embedding vector_cosine_ops)
            WITH (m = 16, ef_construction = 64);
        """))

        conn.execute(text("""
        CREATE INDEX IF NOT EXISTS archivos_vector_promedio_hnsw_idx
            ON archivos
            USING hnsw (vector_promedio vector_cosine_ops)
            WITH (m = 16, ef_construction = 64);
        """))
        conn.execute(text("""
        CREATE INDEX IF NOT EXISTS documentos_embedding_resumen_hnsw_idx
            ON documentos_embedding_resumen
            USING hnsw (embedding vector_cosine_ops)
            WITH (m = 16, ef_construction = 64);
        """))

        conn.execute(text("""
        CREATE INDEX IF NOT EXISTS archivos_vector_promedio_resumen_hnsw_idx
            ON archivos_resumen
            USING hnsw (vector_promedio vector_cosine_ops)
            WITH (m = 16, ef_construction = 64);
        """))
        

        # conn.execute(text("ANALYZE documentos_embedding;"))
    print("✅ Tablas creadas correctamente con pgvector.")


if __name__ == "__main__":
    init_db()
