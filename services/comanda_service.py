from repository.comanda_repository import (
    crear_comanda, ver_comanda_by_id, ver_comandas_por_estado,
    actualizar_estado_comanda, ver_todas_comandas
)
from schemas.comanda_schema import ComandaCreate, ComandaUpdate, EstadoComandaEnum

def crear_comanda_service(comanda: ComandaCreate):
    return crear_comanda(comanda)

def ver_comanda_by_id_service(id_comanda: int):
    return ver_comanda_by_id(id_comanda)

def ver_comandas_por_estado_service(estado: EstadoComandaEnum):
    return ver_comandas_por_estado(estado)

def actualizar_estado_comanda_service(id_comanda: int, estado: EstadoComandaEnum):
    return actualizar_estado_comanda(id_comanda, estado)

def ver_todas_comandas_service():
    return ver_todas_comandas()

