from pydantic import BaseModel
from typing import Optional
from decimal import Decimal

class InsumoBase(BaseModel):
    nombre: str
    descripcion: Optional[str] = None
    unidad_medida: str  # gramos, litros, unidades, etc.
    cantidad_actual: Decimal
    cantidad_minima: Decimal  # Stock mínimo
    precio_compra: Decimal
    activo: bool = True

class InsumoCreate(InsumoBase):
    # nombre_normalizado se genera automáticamente en el repository
    pass

class InsumoUpdate(BaseModel):
    nombre: Optional[str] = None
    descripcion: Optional[str] = None
    unidad_medida: Optional[str] = None
    cantidad_actual: Optional[Decimal] = None
    cantidad_minima: Optional[Decimal] = None
    precio_compra: Optional[Decimal] = None
    activo: Optional[bool] = None

class InsumoResponse(InsumoBase):
    id_insumo: int
    nombre_normalizado: str
    
    class Config:
        from_attributes = True

class MovimientoInventarioBase(BaseModel):
    id_insumo: int
    tipo_movimiento: str  # entrada, salida
    cantidad: Decimal
    motivo: str
    observaciones: Optional[str] = None

class MovimientoInventarioCreate(MovimientoInventarioBase):
    pass

class MovimientoInventarioResponse(MovimientoInventarioBase):
    id_movimiento: int
    fecha_movimiento: str
    
    class Config:
        from_attributes = True

