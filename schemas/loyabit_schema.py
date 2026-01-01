"""
Schemas para integración con Loyabit
"""
from pydantic import BaseModel
from typing import Optional
from decimal import Decimal

class LoyabitClienteCreate(BaseModel):
    """Schema para crear un cliente en Loyabit"""
    nombre: str
    apellido_paterno: str
    apellido_materno: Optional[str] = None
    correo: str
    celular: Optional[str] = None

class LoyabitClienteResponse(BaseModel):
    """Schema para respuesta de cliente desde Loyabit"""
    id: str
    nombre: str
    email: Optional[str] = None
    telefono: Optional[str] = None
    puntos: Optional[Decimal] = None
    # Agregar otros campos según la respuesta de la API de Loyabit

class LoyabitSincronizarCliente(BaseModel):
    """Schema para sincronizar un cliente con Loyabit"""
    id_cliente: int
    forzar_sincronizacion: bool = False  # Si True, actualiza aunque ya esté sincronizado

class LoyabitAgregarPuntos(BaseModel):
    """Schema para agregar puntos a un cliente"""
    id_cliente: int
    puntos: Decimal
    motivo: Optional[str] = "Compra realizada"

class LoyabitCanjearPuntos(BaseModel):
    """Schema para canjear puntos de un cliente"""
    id_cliente: int
    puntos: Decimal
    motivo: Optional[str] = "Canje de puntos"


