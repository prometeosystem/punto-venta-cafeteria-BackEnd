from pydantic import BaseModel
from typing import List, Optional
from decimal import Decimal
from datetime import datetime

class DetalleVentaBase(BaseModel):
    id_producto: int
    cantidad: int
    precio_unitario: Decimal
    subtotal: Decimal

class DetalleVentaCreate(DetalleVentaBase):
    pass

class DetalleVentaResponse(DetalleVentaBase):
    id_detalle_venta: int
    id_venta: int
    
    class Config:
        from_attributes = True

class VentaBase(BaseModel):
    id_cliente: Optional[int] = None
    id_usuario: int  # Vendedor
    total: Decimal
    metodo_pago: str  # efectivo, tarjeta, transferencia
    detalles: List[DetalleVentaCreate]
    
    class Config:
        json_schema_extra = {
            "example": {
                "id_cliente": 1,
                "id_usuario": 2,
                "total": 150.50,
                "metodo_pago": "efectivo",
                "detalles": [
                    {
                        "id_producto": 1,
                        "cantidad": 2,
                        "precio_unitario": 45.00,
                        "subtotal": 90.00
                    },
                    {
                        "id_producto": 3,
                        "cantidad": 1,
                        "precio_unitario": 60.50,
                        "subtotal": 60.50
                    }
                ]
            }
        }

class VentaCreate(VentaBase):
    pass

class VentaResponse(BaseModel):
    id_venta: int
    id_cliente: Optional[int]
    id_usuario: int
    total: Decimal
    metodo_pago: str
    fecha_venta: datetime
    detalles: List[DetalleVentaResponse]
    
    class Config:
        from_attributes = True

