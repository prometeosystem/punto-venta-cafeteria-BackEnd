from repository.cliente_repository import (
    crear_cliente, ver_todos_clientes, ver_cliente_by_id,
    editar_cliente, registrar_visita, ver_visitas_cliente, contar_visitas_cliente
)
from schemas.cliente_schema import VisitaClienteCreate
# TODO: Descomentar cuando se configure la integración con Loyabit
# import os

def crear_cliente_service(cliente, registrar_en_loyabit: bool = None):
    """
    Crea un cliente en la base de datos local.
    TODO: Descomentar cuando se configure la integración con Loyabit
    Si registrar_en_loyabit es True, también lo registra en Loyabit automáticamente.
    Si es None, usa la configuración por defecto (LOYABIT_AUTO_REGISTRO).
    """
    resultado = crear_cliente(cliente)
    
    # Si hay error al crear el cliente, retornar el error
    if isinstance(resultado, dict) and "error" in resultado:
        return resultado
    
    # TODO: Descomentar cuando se configure la integración con Loyabit
    # Ver README_LOYABIT.md para instrucciones de configuración
    # Si se creó correctamente y se debe registrar en Loyabit
    # if resultado.get("id_cliente"):
    #     if registrar_en_loyabit is None:
    #         # Usar configuración por defecto desde variable de entorno
    #         registrar_en_loyabit = os.getenv("LOYABIT_AUTO_REGISTRO", "false").lower() == "true"
    #     
    #     if registrar_en_loyabit:
    #         try:
    #             from services.loyabit_service import registrar_cliente_en_loyabit
    #             resultado_loyabit = registrar_cliente_en_loyabit(resultado["id_cliente"])
    #             # Agregar información de Loyabit al resultado
    #             resultado["loyabit"] = resultado_loyabit
    #         except Exception as e:
    #             # Si falla el registro en Loyabit, no fallar la creación del cliente
    #             resultado["loyabit"] = {"error": f"Error al registrar en Loyabit: {str(e)}", "warning": True}
    
    return resultado

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