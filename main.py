from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import create_engine, Column, Integer, String, Float, Boolean, Text
from sqlalchemy.orm import declarative_base, sessionmaker, Session
from pydantic import BaseModel
from typing import List, Optional

# 1. Configurar la conexión con Neon Tech
DATABASE_URL = "postgresql://neondb_owner:npg_wIcBRfFXSz10@ep-proud-mode-axrxjeme-pooler.c-4.us-east-2.aws.neon.tech/neondb?sslmode=require&channel_binding=require"

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# ----------------------------------------------------
# 2. MODELOS SQLALCHEMY
# ----------------------------------------------------

class PlatilloBD(Base):
    __tablename__ = "platillos"

    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String(100), nullable=False)
    descripcion = Column(String, nullable=True)
    precio = Column(Float, nullable=False)
    disponible = Column(Boolean, default=True)


class ClienteBD(Base):
    __tablename__ = "clientes"

    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String(100), nullable=False)
    telefono = Column(String(20), nullable=True)
    telefono_2 = Column(String(20), nullable=True)
    direccion = Column(String(200), nullable=True)
    referencia = Column(String(200), nullable=True)
    ubicacion = Column(String(500), nullable=True)
    descripcion = Column(Text, nullable=True)  # Agregada importación de Text
    nit = Column(String(20), nullable=True)

# Crea las tablas si no existen
Base.metadata.create_all(bind=engine)

# ----------------------------------------------------
# 3. ESQUEMAS PYDANTIC
# ----------------------------------------------------

# Platillos
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

# Clientes
class ClienteBase(BaseModel):
    nombre: str
    telefono: Optional[str] = None
    telefono_2: Optional[str] = None
    direccion: Optional[str] = None
    referencia: Optional[str] = None
    ubicacion: Optional[str] = None
    descripcion: Optional[str] = None
    nit: Optional[str] = None

class ClienteCrear(ClienteBase):
    pass

class ClienteRespuesta(ClienteBase):
    id: int

    class Config:
        from_attributes = True

# ----------------------------------------------------
# 4. INICIALIZAR APLICACIÓN
# ----------------------------------------------------

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

# ----------------------------------------------------
# 5. ENDPOINTS - PLATILLOS
# ----------------------------------------------------

@app.get("/platillos", response_model=List[PlatilloRespuesta])
def obtener_platillos(db: Session = Depends(get_db)):
    return db.query(PlatilloBD).all()

@app.get("/platillos/buscar", response_model=List[PlatilloRespuesta])
def buscar_platillo(nombre: Optional[str] = "", db: Session = Depends(get_db)):
    if not nombre or nombre.strip() == "":
        return db.query(PlatilloBD).all()
    return db.query(PlatilloBD).filter(PlatilloBD.nombre.ilike(f"%{nombre}%")).all()

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

@app.delete("/platillos/{platillo_id}", status_code=status.HTTP_204_NO_CONTENT)
def eliminar_platillo(platillo_id: int, db: Session = Depends(get_db)):
    platillo_db = db.query(PlatilloBD).filter(PlatilloBD.id == platillo_id).first()
    if not platillo_db:
        raise HTTPException(status_code=404, detail="Platillo no encontrado")
    
    db.delete(platillo_db)
    db.commit()
    return None

# ----------------------------------------------------
# 6. ENDPOINTS - CLIENTES
# ----------------------------------------------------

@app.get("/clientes", response_model=List[ClienteRespuesta])
def obtener_clientes(db: Session = Depends(get_db)):
    return db.query(ClienteBD).all()

@app.get("/clientes/buscar", response_model=List[ClienteRespuesta])
def buscar_cliente(query: Optional[str] = "", db: Session = Depends(get_db)):
    if not query or query.strip() == "":
        return db.query(ClienteBD).all()
    return db.query(ClienteBD).filter(
        (ClienteBD.nombre.ilike(f"%{query}%")) | 
        (ClienteBD.telefono.ilike(f"%{query}%")) |
        (ClienteBD.telefono_2.ilike(f"%{query}%"))
    ).all()

@app.post("/clientes", response_model=ClienteRespuesta)
def crear_cliente(cliente: ClienteCrear, db: Session = Depends(get_db)):
    nuevo_cliente = ClienteBD(**cliente.model_dump())
    db.add(nuevo_cliente)
    db.commit()
    db.refresh(nuevo_cliente)
    return nuevo_cliente

@app.put("/clientes/{cliente_id}", response_model=ClienteRespuesta)
def actualizar_cliente(cliente_id: int, datos: ClienteCrear, db: Session = Depends(get_db)):
    cliente_db = db.query(ClienteBD).filter(ClienteBD.id == cliente_id).first()
    if not cliente_db:
        raise HTTPException(status_code=404, detail="Cliente no encontrado")
    
    for key, value in datos.model_dump().items():
        setattr(cliente_db, key, value)

    db.commit()
    db.refresh(cliente_db)
    return cliente_db

@app.delete("/clientes/{cliente_id}", status_code=status.HTTP_204_NO_CONTENT)
def eliminar_cliente(cliente_id: int, db: Session = Depends(get_db)):
    cliente_db = db.query(ClienteBD).filter(ClienteBD.id == cliente_id).first()
    if not cliente_db:
        raise HTTPException(status_code=404, detail="Cliente no encontrado")
    
    db.delete(cliente_db)
    db.commit()
    return None