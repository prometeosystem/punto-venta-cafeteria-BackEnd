from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class ClienteBase(BaseModel):
    nombre: str
    apellido_paterno: str
    apellido_materno: str
    correo: str
    contrasena: str
    celular: str
    rfc: Optional[str] = None
    direccion: Optional[str] = None
    puntos: float = 0.0

class ClienteCreate(ClienteBase):
    pass

class ClienteUpdate(BaseModel):
    nombre: Optional[str] = None
    apellido_paterno: Optional[str] = None
    apellido_materno: Optional[str] = None
    correo: Optional[str] = None
    contrasena: Optional[str] = None
    celular: Optional[str] = None
    rfc: Optional[str] = None
    direccion: Optional[str] = None
    puntos: Optional[float] = None

class ClienteResponse(ClienteBase):
    id_cliente: int
    
    class Config:
        from_attributes = True

class VisitaClienteBase(BaseModel):
    id_cliente: int
    id_venta: int
    fecha_visita: datetime

class VisitaClienteCreate(VisitaClienteBase):
    pass

class VisitaClienteResponse(VisitaClienteBase):
    id_visita: int
    
    class Config:
        from_attributes = True
