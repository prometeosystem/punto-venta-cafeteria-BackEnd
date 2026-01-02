from repository.cliente_repository import (
    crear_cliente, ver_todos_clientes, ver_cliente_by_id,
    editar_cliente, registrar_visita, ver_visitas_cliente, contar_visitas_cliente
)
from schemas.cliente_schema import VisitaClienteCreate

def crear_cliente_service(cliente):
    return crear_cliente(cliente)

def ver_todos_clientes_service():
    return ver_todos_clientes()

def ver_cliente_by_id_service(id_cliente: int):
    return ver_cliente_by_id(id_cliente)

def editar_cliente_service(id_cliente: int, cliente):
    return editar_cliente(id_cliente, cliente)

def registrar_visita_service(visita: VisitaClienteCreate):
    return registrar_visita(visita)

def ver_visitas_cliente_service(id_cliente: int):
    return ver_visitas_cliente(id_cliente)

def contar_visitas_cliente_service(id_cliente: int):
    return contar_visitas_cliente(id_cliente)