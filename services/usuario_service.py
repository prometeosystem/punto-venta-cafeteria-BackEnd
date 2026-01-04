from repository.usuario_repository import (
    crear_usuario, ver_todos_usuarios, ver_usuario_by_id,
    editar_usuario, eliminar_usuario, obtener_estadisticas_empleados
)
from schemas.usuario_schema import UsuarioCreate, UsuarioUpdate

def crear_usuario_service(usuario: UsuarioCreate):
    return crear_usuario(usuario)

def ver_todos_usuarios_service():
    return ver_todos_usuarios()

def ver_usuario_by_id_service(id_usuario: int):
    return ver_usuario_by_id(id_usuario)

def editar_usuario_service(id_usuario: int, usuario: UsuarioUpdate):
    return editar_usuario(id_usuario, usuario)

def eliminar_usuario_service(id_usuario: int):
    return eliminar_usuario(id_usuario)

def obtener_estadisticas_empleados_service():
    return obtener_estadisticas_empleados()

