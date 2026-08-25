from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import create_engine, Column, Integer, String, Float, Boolean
from sqlalchemy.orm import declarative_base, sessionmaker, Session
from pydantic import BaseModel
from typing import List, Optional

# 1. Configurar la conexión con Neon Tech
DATABASE_URL = "postgresql://neondb_owner:npg_wIcBRfFXSz10@ep-proud-mode-axrxjeme-pooler.c-4.us-east-2.aws.neon.tech/neondb?sslmode=require&channel_binding=require"

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# 2. Definir el modelo de la tabla en SQLAlchemy
class PlatilloBD(Base):
    __tablename__ = "platillos"

    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String(100), nullable=False)
    descripcion = Column(String, nullable=True)
    precio = Column(Float, nullable=False)
    disponible = Column(Boolean, default=True)

# Crea las tablas en Neon Tech si no existen
Base.metadata.create_all(bind=engine)

# 3. Esquemas de Pydantic (para validación de entrada/salida)
class PlatilloBase(BaseModel):
    nombre: str
    descripcion: Optional[str] = None
    precio: float
    disponible: bool = True

class PlatilloCrear(PlatilloBase):
    pass

class PlatilloRespuesta(PlatilloBase):
    id: int

    class Config:
        from_attributes = True

# 4. Inicializar la aplicación FastAPI
app = FastAPI(title="API Sistema de Restaurante")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# 5. Endpoints del Módulo de Productos

# LISTAR TODOS LOS PLATILLOS
@app.get("/platillos", response_model=List[PlatilloRespuesta])
def obtener_platillos(db: Session = Depends(get_db)):
    return db.query(PlatilloBD).all()

# BUSCAR PLATILLOS
@app.get("/platillos/buscar", response_model=List[PlatilloRespuesta])
def buscar_platillo(nombre: str, db: Session = Depends(get_db)):
    return db.query(PlatilloBD).filter(PlatilloBD.nombre.ilike(f"%{nombre}%")).all()

# CREAR NUEVO PLATILLO
@app.post("/platillos", response_model=PlatilloRespuesta)
def crear_platillo(platillo: PlatilloCrear, db: Session = Depends(get_db)):
    nuevo_platillo = PlatilloBD(
        nombre=platillo.nombre,
        descripcion=platillo.descripcion,
        precio=platillo.precio,
        disponible=platillo.disponible
    )
    db.add(nuevo_platillo)
    db.commit()
    db.refresh(nuevo_platillo)
    return nuevo_platillo

# CAMBIAR ESTADO (ACTIVAR / INACTIVAR) O EDITAR
@app.put("/platillos/{platillo_id}", response_model=PlatilloRespuesta)
def actualizar_platillo(platillo_id: int, datos: PlatilloCrear, db: Session = Depends(get_db)):
    platillo_db = db.query(PlatilloBD).filter(PlatilloBD.id == platillo_id).first()
    if not platillo_db:
        raise HTTPException(status_code=404, detail="Platillo no encontrado")
    
    platillo_db.nombre = datos.nombre
    platillo_db.descripcion = datos.descripcion
    platillo_db.precio = datos.precio
    platillo_db.disponible = datos.disponible

    db.commit()
    db.refresh(platillo_db)
    return platillo_db