from fastapi import APIRouter, Depends
from schemas.comanda_schema import RecetaInsumoCreate
from services.receta_service import (
    crear_receta_service,
    ver_recetas_por_producto_service,
    eliminar_receta_service
)
from utils.auth import require_role, get_current_user

router = APIRouter()

@router.post("/crear_receta")
async def crear_receta(
    receta: RecetaInsumoCreate,
    current_user: dict = Depends(require_role(["administrador", "superadministrador"]))
):
    """Crear una receta (relación producto-insumo)"""
    return crear_receta_service(receta)

@router.get("/ver_recetas_producto/{id_producto}")
async def ver_recetas_por_producto(
    id_producto: int,
    current_user: dict = Depends(get_current_user)
):
    """Ver las recetas (insumos) de un producto"""
    return ver_recetas_por_producto_service(id_producto)

@router.delete("/eliminar_receta/{id_receta}")
async def eliminar_receta(
    id_receta: int,
    current_user: dict = Depends(require_role(["administrador", "superadministrador"]))
):
    """Eliminar una receta"""
    return eliminar_receta_service(id_receta)

