from fastapi import APIRouter, Depends, Query
from schemas.comanda_schema import ComandaCreate, ComandaUpdate, EstadoComandaEnum
from services.comanda_service import (
    crear_comanda_service,
    ver_comanda_by_id_service,
    ver_comandas_por_estado_service,
    actualizar_estado_comanda_service,
    ver_todas_comandas_service
)
from utils.auth import require_role, get_current_user

router = APIRouter()

@router.post("/crear_comanda", summary="Crear nueva comanda", response_description="ID de la comanda creada")
async def crear_comanda(
    comanda: ComandaCreate,
    current_user: dict = Depends(require_role(["vendedor", "administrador", "superadministrador"]))
):
    """
    Crear una nueva comanda asociada a una venta.
    
    **Permisos requeridos:** Vendedor, Administrador o Superadministrador
    
    **Notas:**
    - La comanda se crea con estado "pendiente" por defecto
    - Cada detalle debe incluir: `id_producto`, `cantidad`, y opcionalmente `observaciones`
    - La comanda se enviará a cocina para su preparación
    """
    return crear_comanda_service(comanda)

@router.get("/ver_comanda/{id_comanda}", summary="Ver comanda específica")
async def ver_comanda_by_id(
    id_comanda: int,
    current_user: dict = Depends(get_current_user)
):
    """
    Obtener los detalles completos de una comanda específica.
    
    Incluye todos los productos y sus cantidades.
    """
    return ver_comanda_by_id_service(id_comanda)

@router.get("/ver_comandas", summary="Listar comandas")
async def listar_comandas(
    estado: EstadoComandaEnum = Query(None, description="Filtrar por estado de la comanda"),
    current_user: dict = Depends(get_current_user)
):
    """
    Listar todas las comandas o filtrar por estado.
    
    **Estados disponibles:**
    - `pendiente`: Comanda creada, esperando preparación
    - `en_preparacion`: Comanda en proceso de preparación
    - `terminada`: Comanda completada (resta automáticamente insumos del inventario)
    - `cancelada`: Comanda cancelada
    
    Si no se proporciona estado, se retornan todas las comandas.
    """
    if estado:
        return ver_comandas_por_estado_service(estado)
    return ver_todas_comandas_service()

@router.put("/actualizar_estado_comanda/{id_comanda}", summary="Actualizar estado de comanda")
async def actualizar_estado_comanda(
    id_comanda: int,
    estado: EstadoComandaEnum,
    current_user: dict = Depends(require_role(["cocina", "administrador", "superadministrador"]))
):
    """
    Actualizar el estado de una comanda.
    
    **Permisos requeridos:** Cocina, Administrador o Superadministrador
    
    **Importante:**
    - Cuando el estado se cambia a "terminada", se restan automáticamente los insumos del inventario
    - La resta se realiza según las recetas configuradas para cada producto
    - Si no hay suficiente inventario, la operación fallará
    """
    return actualizar_estado_comanda_service(id_comanda, estado)

