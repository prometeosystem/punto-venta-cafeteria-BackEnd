from repository.venta_repository import (
    crear_venta, ver_venta_by_id, ver_todas_ventas, ver_ventas_por_fecha,
    obtener_info_ticket_actual
)
from schemas.venta_schema import VentaCreate

def crear_venta_service(venta: VentaCreate):
    return crear_venta(venta)

def ver_venta_by_id_service(id_venta: int):
    return ver_venta_by_id(id_venta)

def ver_todas_ventas_service():
    return ver_todas_ventas()

def ver_ventas_por_fecha_service(fecha_inicio: str, fecha_fin: str):
    return ver_ventas_por_fecha(fecha_inicio, fecha_fin)

def obtener_info_ticket_actual_service():
    return obtener_info_ticket_actual()

