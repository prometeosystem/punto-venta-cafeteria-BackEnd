from fastapi import APIRouter, Depends, HTTPException, status
from schemas.usuario_schema import UsuarioCreate, UsuarioUpdate, UsuarioResponse
from services.usuario_service import (
    crear_usuario_service,
    ver_todos_usuarios_service,
    ver_usuario_by_id_service,
    editar_usuario_service,
    eliminar_usuario_service
)
from utils.auth import require_role, get_current_user

router = APIRouter()

@router.post("/crear_usuario")
async def crear_usuario(
    usuario: UsuarioCreate,
    current_user: dict = Depends(require_role(["administrador", "superadministrador"]))
):
    """Crear un nuevo usuario (solo administradores)"""
    return crear_usuario_service(usuario)

@router.get("/ver_usuarios")
async def listar_usuarios(
    current_user: dict = Depends(require_role(["administrador", "superadministrador"]))
):
    """Listar todos los usuarios (solo administradores)"""
    return ver_todos_usuarios_service()

@router.get("/ver_usuario/{id_usuario}")
async def ver_usuario_by_id(
    id_usuario: int,
    current_user: dict = Depends(get_current_user)
):
    """Ver un usuario específico"""
    return ver_usuario_by_id_service(id_usuario)

@router.put("/editar_usuario/{id_usuario}")
async def editar_usuario(
    id_usuario: int,
    usuario: UsuarioUpdate,
    current_user: dict = Depends(require_role(["administrador", "superadministrador"]))
):
    """Editar un usuario (solo administradores)"""
    return editar_usuario_service(id_usuario, usuario)

@router.delete("/eliminar_usuario/{id_usuario}")
async def eliminar_usuario(
    id_usuario: int,
    current_user: dict = Depends(require_role(["superadministrador"]))
):
    """Eliminar (desactivar) un usuario (solo superadministrador)"""
    return eliminar_usuario_service(id_usuario)

