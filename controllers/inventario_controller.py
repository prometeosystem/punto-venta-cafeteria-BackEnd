from fastapi import APIRouter, Depends
from schemas.inventario_schema import InsumoCreate, InsumoUpdate, MovimientoInventarioCreate
from services.inventario_service import (
    crear_insumo_service,
    ver_todos_insumos_service,
    ver_insumo_by_id_service,
    editar_insumo_service,
    restar_insumo_service,
    registrar_movimiento_service,
    obtener_insumos_bajo_stock_service
)
from utils.auth import require_role, get_current_user

router = APIRouter()

@router.post("/crear_insumo")
async def crear_insumo(
    insumo: InsumoCreate,
    current_user: dict = Depends(require_role(["administrador", "superadministrador"]))
):
    """Crear un nuevo insumo"""
    return crear_insumo_service(insumo)

@router.get("/ver_insumos")
async def listar_insumos(current_user: dict = Depends(get_current_user)):
    """Listar todos los insumos activos"""
    return ver_todos_insumos_service()

@router.get("/ver_insumo/{id_insumo}")
async def ver_insumo_by_id(
    id_insumo: int,
    current_user: dict = Depends(get_current_user)
):
    """Ver un insumo específico"""
    return ver_insumo_by_id_service(id_insumo)

@router.put("/editar_insumo/{id_insumo}")
async def editar_insumo(
    id_insumo: int,
    insumo: InsumoUpdate,
    current_user: dict = Depends(require_role(["administrador", "superadministrador"]))
):
    """Editar un insumo"""
    return editar_insumo_service(id_insumo, insumo)

@router.post("/registrar_movimiento")
async def registrar_movimiento(
    movimiento: MovimientoInventarioCreate,
    current_user: dict = Depends(require_role(["administrador", "superadministrador"]))
):
    """Registrar un movimiento en el inventario"""
    return registrar_movimiento_service(movimiento)

@router.get("/insumos_bajo_stock")
async def obtener_insumos_bajo_stock(
    current_user: dict = Depends(get_current_user)
):
    """Obtener insumos con stock por debajo del mínimo"""
    return obtener_insumos_bajo_stock_service()

