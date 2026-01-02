from fastapi import APIRouter, Depends, Query
from schemas.preorden_schema import (
    PreordenCreate, PreordenUpdate, EstadoPreordenEnum, PreordenResponse
)
from services.preorden_service import (
    crear_preorden_service,
    ver_preorden_by_id_service,
    ver_preordenes_por_estado_service,
    ver_preordenes_pendientes_service,
    actualizar_preorden_service,
    procesar_pago_preorden_service,
    marcar_preorden_en_cocina_service,
    marcar_preorden_lista_service,
    marcar_preorden_entregada_service
)
from utils.auth import require_role, get_current_user
from pydantic import BaseModel

router = APIRouter()

class ProcesarPagoSchema(BaseModel):
    metodo_pago: str
    id_cliente: int = None

@router.post("/crear_preorden", summary="Crear pre-orden (PÚBLICO)", response_description="ID de la pre-orden creada")
async def crear_preorden(preorden: PreordenCreate):
    """
    **ENDPOINT PÚBLICO** - Crear una pre-orden desde la página web.
    
    Los clientes pueden crear una pre-orden seleccionando productos sin necesidad de autenticación.
    La pre-orden se crea con estado "preorden" y debe pasar por caja para ser procesada.
    
    **Flujo:**
    1. Cliente crea pre-orden (este endpoint)
    2. Cliente pasa a caja
    3. Cajero verifica y asigna nombre del cliente
    4. Cajero procesa el pago
    5. Pre-orden pasa a cocina automáticamente
    6. Cocina marca cuando está lista
    7. Cajero entrega el pedido
    """
    return crear_preorden_service(preorden)

@router.get("/ver_preorden/{id_preorden}", summary="Ver pre-orden específica")
async def ver_preorden_by_id(
    id_preorden: int,
    current_user: dict = Depends(get_current_user)
):
    """
    Obtener los detalles completos de una pre-orden específica.
    
    Requiere autenticación (para cajeros y personal).
    """
    return ver_preorden_by_id_service(id_preorden)

@router.get("/ver_preordenes", summary="Listar pre-órdenes")
async def listar_preordenes(
    estado: EstadoPreordenEnum = Query(None, description="Filtrar por estado de la pre-orden"),
    origen: str = Query(None, description="Filtrar por origen: 'web' o 'sistema'"),
    current_user: dict = Depends(get_current_user)
):
    """
    Listar todas las pre-órdenes o filtrar por estado y origen.
    
    **Estados disponibles:**
    - `preorden`: Creada por el cliente, pendiente de pago
    - `en_caja`: En proceso de pago en caja
    - `pagada`: Pagada, se creó venta y comanda
    - `en_cocina`: En preparación
    - `lista`: Lista para entregar
    - `entregada`: Entregada al cliente
    - `cancelada`: Cancelada
    
    **Origen:**
    - `web`: Pre-órdenes creadas desde la página web (público)
    - `sistema`: Órdenes creadas desde el sistema interno (POS)
    
    Si no se especifica estado, retorna solo pre-órdenes web pendientes (preorden y en_caja).
    """
    if estado:
        return ver_preordenes_por_estado_service(estado, origen)
    # Si no hay estado, retornar solo pre-órdenes web pendientes (preorden y en_caja)
    return ver_preordenes_pendientes_service()

@router.put("/actualizar_preorden/{id_preorden}", summary="Actualizar pre-orden (Cajero)")
async def actualizar_preorden(
    id_preorden: int,
    preorden: PreordenUpdate,
    current_user: dict = Depends(require_role(["vendedor", "administrador", "superadministrador"]))
):
    """
    Actualizar una pre-orden (usado por cajero).
    
    **Permisos requeridos:** Vendedor, Administrador o Superadministrador
    
    Permite:
    - Asignar nombre del cliente
    - Cambiar el estado a "en_caja" cuando el cliente llega a caja
    """
    return actualizar_preorden_service(id_preorden, preorden)

@router.post("/procesar_pago/{id_preorden}", summary="Procesar pago de pre-orden (Cajero)")
async def procesar_pago(
    id_preorden: int,
    pago: ProcesarPagoSchema,
    current_user: dict = Depends(require_role(["vendedor", "administrador", "superadministrador"]))
):
    """
    Procesar el pago de una pre-orden.
    
    **Permisos requeridos:** Vendedor, Administrador o Superadministrador
    
    **Acciones realizadas:**
    1. Crea la venta con los productos de la pre-orden
    2. Crea la comanda asociada a la venta
    3. Actualiza la pre-orden a estado "pagada"
    4. La comanda queda en estado "pendiente" para que cocina la vea
    
    **Parámetros:**
    - `metodo_pago`: efectivo, tarjeta, transferencia
    - `id_cliente`: (opcional) ID del cliente si está registrado
    """
    # Obtener id_usuario del usuario actual, o None si no existe
    id_usuario = current_user.get("id_usuario") if current_user else None
    
    return procesar_pago_preorden_service(
        id_preorden, 
        id_usuario, 
        pago.metodo_pago,
        pago.id_cliente
    )

@router.put("/marcar_en_cocina/{id_preorden}", summary="Marcar pre-orden en cocina")
async def marcar_en_cocina(
    id_preorden: int,
    current_user: dict = Depends(require_role(["cocina", "administrador", "superadministrador"]))
):
    """
    Marcar una pre-orden como en cocina (cuando la comanda está en preparación).
    
    **Permisos requeridos:** Cocina, Administrador o Superadministrador
    """
    return marcar_preorden_en_cocina_service(id_preorden)

@router.put("/marcar_lista/{id_preorden}", summary="Marcar pre-orden como lista (Cocina)")
async def marcar_lista(
    id_preorden: int,
    current_user: dict = Depends(require_role(["cocina", "administrador", "superadministrador"]))
):
    """
    Marcar una pre-orden como lista para entregar.
    
    **Permisos requeridos:** Cocina, Administrador o Superadministrador
    
    Cuando cocina marca la comanda como terminada, esta pre-orden se marca como "lista"
    para que el cajero sepa que puede entregarla.
    """
    return marcar_preorden_lista_service(id_preorden)

@router.put("/marcar_entregada/{id_preorden}", summary="Marcar pre-orden como entregada (Cajero)")
async def marcar_entregada(
    id_preorden: int,
    current_user: dict = Depends(require_role(["vendedor", "administrador", "superadministrador"]))
):
    """
    Marcar una pre-orden como entregada al cliente.
    
    **Permisos requeridos:** Vendedor, Administrador o Superadministrador
    
    El cajero marca la pre-orden como entregada cuando entrega el pedido al cliente.
    """
    return marcar_preorden_entregada_service(id_preorden)


