from pydantic import BaseModel
from typing import List, Optional
from decimal import Decimal
from datetime import datetime
from enum import Enum

class EstadoPreordenEnum(str, Enum):
    PREORDEN = "preorden"  # Creada por el cliente, pendiente de pago
    EN_CAJA = "en_caja"  # En proceso de pago en caja
    PAGADA = "pagada"  # Pagada, se crea venta y comanda
    EN_COCINA = "en_cocina"  # En preparación
    LISTA = "lista"  # Lista para entregar
    ENTREGADA = "entregada"  # Entregada al cliente
    CANCELADA = "cancelada"  # Cancelada

class DetallePreordenBase(BaseModel):
    id_producto: int
    cantidad: int
    observaciones: Optional[str] = None

class DetallePreordenCreate(DetallePreordenBase):
    pass

class DetallePreordenResponse(DetallePreordenBase):
    id_detalle_preorden: int
    id_preorden: int
    
    class Config:
        from_attributes = True

class PreordenBase(BaseModel):
    nombre_cliente: Optional[str] = None
    detalles: List[DetallePreordenCreate]

class PreordenCreate(PreordenBase):
    """Schema para crear una pre-orden desde la página web (público)"""
    tipo_servicio: Optional[str] = None  # "comer-aqui" o "para-llevar"
    comentarios: Optional[str] = None  # Comentarios generales del pedido
    tipo_leche: Optional[str] = None  # "entera" o "deslactosada" (solo si hay bebidas)
    extra_leche: Optional[Decimal] = None  # Monto extra ($15) por leche deslactosada

class PreordenUpdate(BaseModel):
    """Schema para actualizar una pre-orden (cajero asigna cliente)"""
    nombre_cliente: Optional[str] = None
    estado: Optional[EstadoPreordenEnum] = None

class PreordenResponse(BaseModel):
    id_preorden: int
    nombre_cliente: Optional[str]
    estado: EstadoPreordenEnum
    total: Optional[Decimal] = None
    id_venta: Optional[int] = None  # Se asigna cuando se paga
    ticket_id: Optional[str] = None  # ID único de ticket cuando se procesa el pago
    origen: Optional[str] = None  # "web" o "sistema"
    tipo_servicio: Optional[str] = None
    comentarios: Optional[str] = None
    tipo_leche: Optional[str] = None
    extra_leche: Optional[Decimal] = None
    fecha_creacion: datetime
    fecha_actualizacion: Optional[datetime]
    detalles: List[DetallePreordenResponse]
    
    class Config:
        from_attributes = True


