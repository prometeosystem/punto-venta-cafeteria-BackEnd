"""
Servicio para integración con Loyabit
"""
from repository.cliente_repository import (
    ver_cliente_by_id, actualizar_loyabit_id, obtener_cliente_por_loyabit_id
)
from utils.loyabit_client import get_loyabit_client
from decimal import Decimal
from typing import Optional, Dict, Any

def registrar_cliente_en_loyabit(id_cliente: int) -> Dict[str, Any]:
    """
    Registra un cliente en Loyabit y actualiza su ID en la base de datos
    
    Args:
        id_cliente: ID del cliente en la base de datos local
        
    Returns:
        Diccionario con el resultado de la operación
    """
    # Obtener datos del cliente
    cliente_local = ver_cliente_by_id(id_cliente)
    if isinstance(cliente_local, dict) and "error" in cliente_local:
        return cliente_local
    
    # Si ya está sincronizado, no hacer nada (a menos que se fuerce)
    if cliente_local.get("loyabit_sincronizado") and cliente_local.get("loyabit_id"):
        return {
            "message": "Cliente ya está registrado en Loyabit",
            "loyabit_id": cliente_local["loyabit_id"],
            "ya_existia": True
        }
    
    # Verificar si ya existe en Loyabit por email
    loyabit_client = get_loyabit_client()
    
    try:
        cliente_loyabit = loyabit_client.buscar_cliente_por_email(cliente_local["correo"])
        
        if cliente_loyabit:
            # El cliente ya existe en Loyabit, solo actualizar el ID local
            loyabit_id = cliente_loyabit.get("id") or cliente_loyabit.get("customer_id")  # Ajustar según la respuesta
            resultado = actualizar_loyabit_id(id_cliente, loyabit_id, True)
            return {
                "message": "Cliente encontrado en Loyabit y vinculado",
                "loyabit_id": loyabit_id,
                "ya_existia": True
            }
        
        # Crear cliente en Loyabit
        cliente_data = {
            "nombre": cliente_local["nombre"],
            "apellido_paterno": cliente_local["apellido_paterno"],
            "apellido_materno": cliente_local.get("apellido_materno", ""),
            "correo": cliente_local["correo"],
            "celular": cliente_local.get("celular", ""),
        }
        
        respuesta_loyabit = loyabit_client.crear_cliente(cliente_data)
        loyabit_id = respuesta_loyabit.get("id") or respuesta_loyabit.get("customer_id")  # Ajustar según la respuesta
        
        # Actualizar el ID de Loyabit en la base de datos local
        resultado = actualizar_loyabit_id(id_cliente, loyabit_id, True)
        
        if "error" in resultado:
            return resultado
        
        return {
            "message": "Cliente registrado correctamente en Loyabit",
            "loyabit_id": loyabit_id,
            "ya_existia": False
        }
        
    except Exception as e:
        return {
            "error": f"Error al registrar cliente en Loyabit: {str(e)}"
        }

def obtener_info_cliente_loyabit(id_cliente: int) -> Dict[str, Any]:
    """
    Obtiene información de un cliente desde Loyabit
    
    Args:
        id_cliente: ID del cliente en la base de datos local
        
    Returns:
        Diccionario con la información del cliente desde Loyabit
    """
    cliente_local = ver_cliente_by_id(id_cliente)
    if isinstance(cliente_local, dict) and "error" in cliente_local:
        return cliente_local
    
    loyabit_id = cliente_local.get("loyabit_id")
    if not loyabit_id:
        return {
            "error": "Cliente no está registrado en Loyabit. Regístrelo primero.",
            "sincronizar_primero": True
        }
    
    loyabit_client = get_loyabit_client()
    
    try:
        info_cliente = loyabit_client.obtener_cliente(loyabit_id)
        puntos = loyabit_client.obtener_puntos_cliente(loyabit_id)
        
        return {
            "cliente": info_cliente,
            "puntos": puntos,
            "loyabit_id": loyabit_id
        }
    except Exception as e:
        return {
            "error": f"Error al obtener información del cliente desde Loyabit: {str(e)}"
        }

def sincronizar_cliente_con_loyabit(id_cliente: int, forzar: bool = False) -> Dict[str, Any]:
    """
    Sincroniza un cliente con Loyabit (registra si no existe, actualiza si existe)
    
    Args:
        id_cliente: ID del cliente en la base de datos local
        forzar: Si True, actualiza aunque ya esté sincronizado
        
    Returns:
        Diccionario con el resultado de la sincronización
    """
    cliente_local = ver_cliente_by_id(id_cliente)
    if isinstance(cliente_local, dict) and "error" in cliente_local:
        return cliente_local
    
    loyabit_client = get_loyabit_client()
    
    try:
        # Si ya tiene loyabit_id, actualizar
        if cliente_local.get("loyabit_id") and not forzar:
            try:
                # Actualizar información en Loyabit
                cliente_data = {
                    "nombre": cliente_local["nombre"],
                    "apellido_paterno": cliente_local["apellido_paterno"],
                    "apellido_materno": cliente_local.get("apellido_materno", ""),
                    "correo": cliente_local["correo"],
                    "celular": cliente_local.get("celular", ""),
                }
                loyabit_client.actualizar_cliente(cliente_local["loyabit_id"], cliente_data)
                
                return {
                    "message": "Cliente actualizado en Loyabit",
                    "loyabit_id": cliente_local["loyabit_id"],
                    "accion": "actualizado"
                }
            except Exception as e:
                # Si falla la actualización, intentar registrar de nuevo
                return registrar_cliente_en_loyabit(id_cliente)
        
        # Registrar nuevo cliente
        return registrar_cliente_en_loyabit(id_cliente)
        
    except Exception as e:
        return {
            "error": f"Error al sincronizar cliente con Loyabit: {str(e)}"
        }

def agregar_puntos_loyabit(id_cliente: int, puntos: Decimal, motivo: str = "Compra realizada") -> Dict[str, Any]:
    """
    Agrega puntos a un cliente en Loyabit
    
    Args:
        id_cliente: ID del cliente en la base de datos local
        puntos: Cantidad de puntos a agregar
        motivo: Motivo por el cual se agregan puntos
        
    Returns:
        Diccionario con el resultado de la operación
    """
    cliente_local = ver_cliente_by_id(id_cliente)
    if isinstance(cliente_local, dict) and "error" in cliente_local:
        return cliente_local
    
    loyabit_id = cliente_local.get("loyabit_id")
    if not loyabit_id:
        return {
            "error": "Cliente no está registrado en Loyabit. Regístrelo primero.",
            "sincronizar_primero": True
        }
    
    loyabit_client = get_loyabit_client()
    
    try:
        respuesta = loyabit_client.agregar_puntos(loyabit_id, float(puntos), motivo)
        return {
            "message": f"Puntos agregados correctamente en Loyabit",
            "puntos_agregados": puntos,
            "respuesta_loyabit": respuesta
        }
    except Exception as e:
        return {
            "error": f"Error al agregar puntos en Loyabit: {str(e)}"
        }

def canjear_puntos_loyabit(id_cliente: int, puntos: Decimal, motivo: str = "Canje de puntos") -> Dict[str, Any]:
    """
    Canjea puntos de un cliente en Loyabit
    
    Args:
        id_cliente: ID del cliente en la base de datos local
        puntos: Cantidad de puntos a canjear
        motivo: Motivo del canje
        
    Returns:
        Diccionario con el resultado de la operación
    """
    cliente_local = ver_cliente_by_id(id_cliente)
    if isinstance(cliente_local, dict) and "error" in cliente_local:
        return cliente_local
    
    loyabit_id = cliente_local.get("loyabit_id")
    if not loyabit_id:
        return {
            "error": "Cliente no está registrado en Loyabit. Regístrelo primero.",
            "sincronizar_primero": True
        }
    
    loyabit_client = get_loyabit_client()
    
    try:
        respuesta = loyabit_client.canjear_puntos(loyabit_id, float(puntos), motivo)
        return {
            "message": f"Puntos canjeados correctamente en Loyabit",
            "puntos_canjeados": puntos,
            "respuesta_loyabit": respuesta
        }
    except Exception as e:
        return {
            "error": f"Error al canjear puntos en Loyabit: {str(e)}"
        }


