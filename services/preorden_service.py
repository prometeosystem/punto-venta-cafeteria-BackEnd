from repository.preorden_repository import (
    crear_preorden, ver_preorden_by_id, ver_preordenes_por_estado,
    ver_preordenes_pendientes, actualizar_preorden, procesar_pago_preorden,
    marcar_preorden_en_cocina, marcar_preorden_lista, marcar_preorden_entregada
)
from schemas.preorden_schema import PreordenCreate, PreordenUpdate, EstadoPreordenEnum

def crear_preorden_service(preorden: PreordenCreate):
    return crear_preorden(preorden)

def ver_preorden_by_id_service(id_preorden: int):
    return ver_preorden_by_id(id_preorden)

def ver_preordenes_por_estado_service(estado: EstadoPreordenEnum, origen: str = None):
    return ver_preordenes_por_estado(estado, origen)

def ver_preordenes_pendientes_service():
    return ver_preordenes_pendientes()

def actualizar_preorden_service(id_preorden: int, preorden: PreordenUpdate):
    return actualizar_preorden(id_preorden, preorden)

def procesar_pago_preorden_service(id_preorden: int, id_usuario: int, metodo_pago: str, id_cliente: int = None):
    return procesar_pago_preorden(id_preorden, id_usuario, metodo_pago, id_cliente)

def marcar_preorden_en_cocina_service(id_preorden: int):
    return marcar_preorden_en_cocina(id_preorden)

def marcar_preorden_lista_service(id_preorden: int):
    return marcar_preorden_lista(id_preorden)

def marcar_preorden_entregada_service(id_preorden: int):
    return marcar_preorden_entregada(id_preorden)


