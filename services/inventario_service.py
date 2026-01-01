from repository.inventario_repository import (
    crear_insumo, ver_todos_insumos, ver_insumo_by_id,
    editar_insumo, restar_insumo, registrar_movimiento,
    obtener_insumos_bajo_stock, ver_insumos_normalizados, buscar_insumo_por_nombre
)
from schemas.inventario_schema import InsumoCreate, InsumoUpdate, MovimientoInventarioCreate

def crear_insumo_service(insumo: InsumoCreate):
    return crear_insumo(insumo)

def ver_todos_insumos_service():
    return ver_todos_insumos()

def ver_insumo_by_id_service(id_insumo: int):
    return ver_insumo_by_id(id_insumo)

def editar_insumo_service(id_insumo: int, insumo: InsumoUpdate):
    return editar_insumo(id_insumo, insumo)

def restar_insumo_service(id_insumo: int, cantidad: float):
    return restar_insumo(id_insumo, cantidad)

def registrar_movimiento_service(movimiento: MovimientoInventarioCreate):
    return registrar_movimiento(movimiento)

def obtener_insumos_bajo_stock_service():
    return obtener_insumos_bajo_stock()

def ver_insumos_normalizados_service():
    return ver_insumos_normalizados()

def buscar_insumo_por_nombre_service(nombre: str):
    return buscar_insumo_por_nombre(nombre)

