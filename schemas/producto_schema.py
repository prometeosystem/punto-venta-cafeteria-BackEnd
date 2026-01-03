from pydantic import BaseModel, field_validator, model_validator
from typing import Optional, List
from decimal import Decimal

class ProductoBase(BaseModel):
    nombre: str
    descripcion: Optional[str] = None
    precio: Decimal
    categoria: str
    activo: bool = True

# Esquema para crear un insumo nuevo desde la creación de producto
# Solo datos básicos - sin unidad de medida (va en la receta)
class InsumoNuevoCreate(BaseModel):
    nombre: str
    descripcion: Optional[str] = None

# Esquema para relacionar insumo con producto (puede ser existente o nuevo)
# La unidad de medida va aquí porque es específica de cómo se usa en este producto
class RecetaInsumoEnProducto(BaseModel):
    # Si id_insumo está presente, usa insumo existente
    id_insumo: Optional[int] = None
    # Si insumo_nuevo está presente, crea el insumo primero
    insumo_nuevo: Optional[InsumoNuevoCreate] = None
    cantidad_necesaria: Decimal
    unidad_medida: str  # gramos, kg, litros, mililitros, onzas, piezas, unidades, etc.
    
    @model_validator(mode='after')
    def validate_insumo(self):
        """Valida que se proporcione id_insumo O insumo_nuevo, pero no ambos ni ninguno"""
        if not self.id_insumo and not self.insumo_nuevo:
            raise ValueError("Debe proporcionar 'id_insumo' o 'insumo_nuevo'")
        if self.id_insumo and self.insumo_nuevo:
            raise ValueError("No puede proporcionar 'id_insumo' e 'insumo_nuevo' al mismo tiempo")
        return self

class ProductoCreate(ProductoBase):
    # Lista opcional de insumos/recetas para el producto
    recetas: Optional[List[RecetaInsumoEnProducto]] = None

class ProductoUpdate(BaseModel):
    nombre: Optional[str] = None
    descripcion: Optional[str] = None
    precio: Optional[Decimal] = None
    categoria: Optional[str] = None
    activo: Optional[bool] = None
    # Lista opcional de recetas para actualizar (si se proporciona, reemplaza todas las recetas existentes)
    recetas: Optional[List[RecetaInsumoEnProducto]] = None

class ProductoResponse(ProductoBase):
    id_producto: int
    
    class Config:
        from_attributes = True

