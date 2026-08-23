from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import create_engine, Column, Integer, String, Float, Boolean
from sqlalchemy.orm import declarative_base, sessionmaker, Session

# 1. Configurar la conexión con Neon Tech
DATABASE_URL = "postgresql://neondb_owner:npg_wIcBRfFXSz10@ep-proud-mode-axrxjeme-pooler.c-4.us-east-2.aws.neon.tech/neondb?sslmode=require&channel_binding=require"

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# 2. Definir el modelo de la tabla en Python
class PlatilloBD(Base):
    __tablename__ = "platillos"

    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String(100), nullable=False)
    descripcion = Column(String)
    precio = Column(Float, nullable=False)
    disponible = Column(Boolean, default=True)

# 3. Inicializar la aplicación FastAPI
app = FastAPI(title="API Sistema de Restaurante")

# Habilitar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Función para obtener sesión de Base de Datos
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# 4. Endpoint para buscar platillos por coincidencia de nombre
@app.get("/platillos/buscar")
def buscar_platillo(nombre: str, db: Session = Depends(get_db)):
    # ILIKE permite buscar coincidencias sin importar mayúsculas o minúsculas
    resultados = db.query(PlatilloBD).filter(PlatilloBD.nombre.ilike(f"%{nombre}%")).all()
    return resultados