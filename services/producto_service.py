from repository.producto_repository import (
    crear_producto, ver_todos_productos, ver_producto_by_id,
    editar_producto, eliminar_producto
)
from schemas.producto_schema import ProductoCreate, ProductoUpdate

def crear_producto_service(producto: ProductoCreate):
    return crear_producto(producto)

def ver_todos_productos_service():
    return ver_todos_productos()

def ver_producto_by_id_service(id_producto: int):
    return ver_producto_by_id(id_producto)

def editar_producto_service(id_producto: int, producto: ProductoUpdate):
    return editar_producto(id_producto, producto)

def eliminar_producto_service(id_producto: int):
    return eliminar_producto(id_producto)

