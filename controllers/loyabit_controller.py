"""
Controlador para integración con Loyabit
"""
from fastapi import APIRouter, Depends
from schemas.loyabit_schema import (
    LoyabitSincronizarCliente, LoyabitAgregarPuntos, LoyabitCanjearPuntos
)
from services.loyabit_service import (
    registrar_cliente_en_loyabit,
    obtener_info_cliente_loyabit,
    sincronizar_cliente_con_loyabit,
    agregar_puntos_loyabit,
    canjear_puntos_loyabit
)
from utils.auth import require_role, get_current_user

router = APIRouter()

@router.post("/registrar_cliente/{id_cliente}")
async def registrar_cliente_loyabit(
    id_cliente: int,
    current_user: dict = Depends(require_role(["administrador", "superadministrador"]))
):
    """
    Registra un cliente en Loyabit.
    Si el cliente ya existe en Loyabit (por email), solo lo vincula.
    """
    return registrar_cliente_en_loyabit(id_cliente)

@router.get("/info_cliente/{id_cliente}")
async def obtener_info_cliente(
    id_cliente: int,
    current_user: dict = Depends(get_current_user)
):
    """
    Obtiene información de un cliente desde Loyabit (incluye puntos).
    Requiere que el cliente esté registrado en Loyabit.
    """
    return obtener_info_cliente_loyabit(id_cliente)

@router.post("/sincronizar_cliente")
async def sincronizar_cliente(
    datos: LoyabitSincronizarCliente,
    current_user: dict = Depends(require_role(["administrador", "superadministrador"]))
):
    """
    Sincroniza un cliente con Loyabit.
    - Si no está registrado, lo registra
    - Si ya está registrado, actualiza su información
    """
    return sincronizar_cliente_con_loyabit(
        datos.id_cliente,
        datos.forzar_sincronizacion
    )

@router.post("/agregar_puntos")
async def agregar_puntos(
    datos: LoyabitAgregarPuntos,
    current_user: dict = Depends(require_role(["vendedor", "administrador", "superadministrador"]))
):
    """
    Agrega puntos a un cliente en Loyabit.
    Útil después de una compra para acumular puntos de fidelidad.
    """
    return agregar_puntos_loyabit(
        datos.id_cliente,
        datos.puntos,
        datos.motivo
    )

@router.post("/canjear_puntos")
async def canjear_puntos(
    datos: LoyabitCanjearPuntos,
    current_user: dict = Depends(require_role(["vendedor", "administrador", "superadministrador"]))
):
    """
    Canjea puntos de un cliente en Loyabit.
    Útil cuando un cliente usa sus puntos para obtener un descuento o premio.
    """
    return canjear_puntos_loyabit(
        datos.id_cliente,
        datos.puntos,
        datos.motivo
    )


