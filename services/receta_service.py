from repository.receta_repository import (
    crear_receta, ver_recetas_por_producto, eliminar_receta
)
from schemas.comanda_schema import RecetaInsumoCreate

def crear_receta_service(receta: RecetaInsumoCreate):
    return crear_receta(receta)

def ver_recetas_por_producto_service(id_producto: int):
    return ver_recetas_por_producto(id_producto)

def eliminar_receta_service(id_receta: int):
    return eliminar_receta(id_receta)

