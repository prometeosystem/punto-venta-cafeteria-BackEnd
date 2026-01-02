from fastapi import APIRouter, Depends
from schemas.producto_schema import ProductoCreate, ProductoUpdate
from services.producto_service import (
    crear_producto_service,
    ver_todos_productos_service,
    ver_producto_by_id_service,
    editar_producto_service,
    eliminar_producto_service
)
from utils.auth import require_role, get_current_user

router = APIRouter()

@router.post("/crear_producto")
async def crear_producto(
    producto: ProductoCreate,
    current_user: dict = Depends(require_role(["administrador", "superadministrador"]))
):
    """Crear un nuevo producto"""
    return crear_producto_service(producto)

@router.get("/ver_productos", summary="Listar productos (PÚBLICO)")
async def listar_productos():
    """
    **ENDPOINT PÚBLICO** - Listar todos los productos activos.
    
    No requiere autenticación. Usado por la página web para mostrar el menú.
    """
    return ver_todos_productos_service()

@router.get("/ver_producto/{id_producto}")
async def ver_producto_by_id(
    id_producto: int,
    current_user: dict = Depends(get_current_user)
):
    """Ver un producto específico"""
    return ver_producto_by_id_service(id_producto)

@router.put("/editar_producto/{id_producto}")
async def editar_producto(
    id_producto: int,
    producto: ProductoUpdate,
    current_user: dict = Depends(require_role(["administrador", "superadministrador"]))
):
    """Editar un producto"""
    return editar_producto_service(id_producto, producto)

@router.delete("/eliminar_producto/{id_producto}")
async def eliminar_producto(
    id_producto: int,
    current_user: dict = Depends(require_role(["administrador", "superadministrador"]))
):
    """Eliminar (desactivar) un producto"""
    return eliminar_producto_service(id_producto)

