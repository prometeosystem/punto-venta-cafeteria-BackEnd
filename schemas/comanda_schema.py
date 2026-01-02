from pydantic import BaseModel
from typing import List, Optional
from decimal import Decimal
from datetime import datetime
from enum import Enum

class EstadoComandaEnum(str, Enum):
    PENDIENTE = "pendiente"
    EN_PREPARACION = "en_preparacion"  # También actualiza pre-orden a "en_cocina"
    TERMINADA = "terminada"  # También actualiza pre-orden a "lista"
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
    producto_nombre: Optional[str] = None  # Nombre del producto para mostrar
    
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

class PreordenInfoComanda(BaseModel):
    """Información del pedido asociado a la comanda"""
    id_preorden: Optional[int] = None
    origen: Optional[str] = None  # 'web' o 'sistema'
    ticket_id: Optional[str] = None  # ID único del ticket
    nombre_cliente: Optional[str] = None
    tipo_servicio: Optional[str] = None  # 'comer-aqui' o 'para-llevar'
    tipo_leche: Optional[str] = None  # 'entera' o 'deslactosada'
    extra_leche: Optional[Decimal] = None  # Monto extra por leche deslactosada
    comentarios: Optional[str] = None  # Comentarios generales del pedido
    
    class Config:
        from_attributes = True

class ComandaResponse(BaseModel):
    id_comanda: int
    id_venta: int
    estado: EstadoComandaEnum
    fecha_creacion: datetime
    fecha_actualizacion: Optional[datetime]
    total: Optional[Decimal] = None  # Total de la venta
    fecha_venta: Optional[datetime] = None  # Fecha de la venta
    detalles: List[DetalleComandaResponse]
    preorden: Optional[PreordenInfoComanda] = None  # Información completa del pedido
    
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

