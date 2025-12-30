from pydantic import BaseModel
from typing import List, Optional
from decimal import Decimal
from datetime import datetime
from enum import Enum

class EstadoComandaEnum(str, Enum):
    PENDIENTE = "pendiente"
    EN_PREPARACION = "en_preparacion"
    TERMINADA = "terminada"
    CANCELADA = "cancelada"

class DetalleComandaBase(BaseModel):
    id_producto: int
    cantidad: int
    observaciones: Optional[str] = None

class DetalleComandaCreate(DetalleComandaBase):
    pass

class DetalleComandaResponse(DetalleComandaBase):
    id_detalle_comanda: int
    id_comanda: int
    
    class Config:
        from_attributes = True

class ComandaBase(BaseModel):
    id_venta: int
    estado: EstadoComandaEnum = EstadoComandaEnum.PENDIENTE
    detalles: List[DetalleComandaCreate]
    
    class Config:
        json_schema_extra = {
            "example": {
                "id_venta": 1,
                "estado": "pendiente",
                "detalles": [
                    {
                        "id_producto": 1,
                        "cantidad": 2,
                        "observaciones": "Sin azúcar"
                    },
                    {
                        "id_producto": 3,
                        "cantidad": 1,
                        "observaciones": "Extra caliente"
                    }
                ]
            }
        }

class ComandaCreate(ComandaBase):
    pass

class ComandaUpdate(BaseModel):
    estado: Optional[EstadoComandaEnum] = None

class ComandaResponse(BaseModel):
    id_comanda: int
    id_venta: int
    estado: EstadoComandaEnum
    fecha_creacion: datetime
    fecha_actualizacion: Optional[datetime]
    detalles: List[DetalleComandaResponse]
    
    class Config:
        from_attributes = True

class RecetaInsumoBase(BaseModel):
    id_producto: int
    id_insumo: int
    cantidad_necesaria: Decimal

class RecetaInsumoCreate(RecetaInsumoBase):
    pass

class RecetaInsumoResponse(RecetaInsumoBase):
    id_receta: int
    
    class Config:
        from_attributes = True

