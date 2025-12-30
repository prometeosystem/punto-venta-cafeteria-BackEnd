from fastapi import APIRouter, Depends
from schemas.cliente_schema import ClienteBase, ClienteUpdate, VisitaClienteCreate
from services.cliente_service import (
    crear_cliente_service,
    ver_todos_clientes_service,
    ver_cliente_by_id_service,
    editar_cliente_service,
    registrar_visita_service,
    ver_visitas_cliente_service,
    contar_visitas_cliente_service
)
from utils.auth import get_current_user, require_role

router = APIRouter()

@router.post("/crear_cliente")
async def crear_cliente(cliente: ClienteBase):
    """Crear un nuevo cliente"""
    return crear_cliente_service(cliente)

@router.get("/ver_clientes")
async def listar_clientes(current_user: dict = Depends(get_current_user)):
    """Listar todos los clientes"""
    return ver_todos_clientes_service()

@router.get("/ver_cliente/{id_cliente}")
async def ver_cliente_by_id(
    id_cliente: int,
    current_user: dict = Depends(get_current_user)
):
    """Ver un cliente específico"""
    return ver_cliente_by_id_service(id_cliente)

@router.put("/editar_cliente/{id_cliente}")
async def editar_cliente(
    id_cliente: int,
    cliente: ClienteUpdate,
    current_user: dict = Depends(require_role(["administrador", "superadministrador"]))
):
    """Editar un cliente"""
    return editar_cliente_service(id_cliente, cliente)

@router.post("/registrar_visita")
async def registrar_visita(
    visita: VisitaClienteCreate,
    current_user: dict = Depends(require_role(["vendedor", "administrador", "superadministrador"]))
):
    """Registrar una visita de un cliente (para tarjeta de fidelidad)"""
    return registrar_visita_service(visita)

@router.get("/visitas_cliente/{id_cliente}")
async def ver_visitas_cliente(
    id_cliente: int,
    current_user: dict = Depends(get_current_user)
):
    """Ver todas las visitas de un cliente"""
    return ver_visitas_cliente_service(id_cliente)

@router.get("/contar_visitas_cliente/{id_cliente}")
async def contar_visitas_cliente(
    id_cliente: int,
    current_user: dict = Depends(get_current_user)
):
    """Contar el total de visitas de un cliente"""
    return contar_visitas_cliente_service(id_cliente)