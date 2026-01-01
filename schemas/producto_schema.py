from pydantic import BaseModel
from typing import Optional, List
from decimal import Decimal

class InsumoRecetaBase(BaseModel):
    """Schema para un insumo en una receta"""
    nombre_insumo: str  # Nombre del insumo (se buscará por nombre normalizado)
    cantidad_necesaria: Decimal
    unidad_medida: str  # Debe coincidir con la unidad del insumo

class InsumoRecetaCreate(InsumoRecetaBase):
    """Para crear un insumo nuevo si no existe"""
    crear_si_no_existe: bool = False  # Si es True y no existe, se crea
    descripcion: Optional[str] = None
    cantidad_actual: Optional[Decimal] = Decimal(0)  # Solo si se crea nuevo
    cantidad_minima: Optional[Decimal] = Decimal(0)  # Solo si se crea nuevo
    precio_compra: Optional[Decimal] = Decimal(0)  # Solo si se crea nuevo

class ProductoBase(BaseModel):
    nombre: str
    descripcion: Optional[str] = None
    precio: Decimal
    categoria: str
    tiempo_preparacion: Optional[int] = None  # Tiempo en minutos
    activo: bool = True

class ProductoCreate(ProductoBase):
    insumos: Optional[List[InsumoRecetaCreate]] = []  # Lista de insumos para la receta

class ProductoUpdate(BaseModel):
    nombre: Optional[str] = None
    descripcion: Optional[str] = None
    precio: Optional[Decimal] = None
    categoria: Optional[str] = None
    tiempo_preparacion: Optional[int] = None
    activo: Optional[bool] = None

class ProductoResponse(ProductoBase):
    id_producto: int
    
    class Config:
        from_attributes = True

