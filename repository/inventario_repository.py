from database.conexion import conectar
from schemas.inventario_schema import InsumoCreate, InsumoUpdate, MovimientoInventarioCreate
from datetime import datetime
from decimal import Decimal
from typing import Optional
from utils.normalize import normalizar_nombre

def crear_insumo(insumo: InsumoCreate):
    conexion = conectar()
    if not conexion:
        return {"error": "Error de conexión a la base de datos"}
    
    cursor = conexion.cursor()
    
    # Normalizar nombre
    nombre_normalizado = normalizar_nombre(insumo.nombre)
    
    # Verificar si ya existe un insumo con el mismo nombre normalizado
    sql_check = "SELECT id_insumo, nombre FROM insumos WHERE nombre_normalizado = %s"
    cursor.execute(sql_check, (nombre_normalizado,))
    existente = cursor.fetchone()
    if existente:
        cursor.close()
        conexion.close()
        return {
            "error": f"Ya existe un insumo con nombre similar: '{existente[1]}' (id: {existente[0]})",
            "id_insumo_existente": existente[0]
        }
    
    sql = """
    INSERT INTO insumos(
        nombre, nombre_normalizado, descripcion, unidad_medida, cantidad_actual,
        cantidad_minima, precio_compra, activo
    )
    VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
    """
    datos = (
        insumo.nombre, nombre_normalizado, insumo.descripcion, insumo.unidad_medida,
        insumo.cantidad_actual, insumo.cantidad_minima,
        insumo.precio_compra, insumo.activo
    )
    
    try:
        cursor.execute(sql, datos)
        conexion.commit()
        insumo_id = cursor.lastrowid
        cursor.close()
        conexion.close()
        return {"message": "Insumo creado correctamente", "id_insumo": insumo_id}
    except Exception as e:
        conexion.rollback()
        cursor.close()
        conexion.close()
        return {"error": f"Error al crear insumo: {str(e)}"}

def buscar_insumo_por_nombre(nombre: str):
    """Busca un insumo por nombre normalizado"""
    conexion = conectar()
    if not conexion:
        return None
    
    nombre_normalizado = normalizar_nombre(nombre)
    cursor = conexion.cursor(dictionary=True)
    sql = "SELECT * FROM insumos WHERE nombre_normalizado = %s AND activo = 1"
    cursor.execute(sql, (nombre_normalizado,))
    insumo = cursor.fetchone()
    cursor.close()
    conexion.close()
    return insumo

def obtener_insumo_o_crear(nombre: str, unidad_medida: str, cantidad_actual: Decimal = Decimal(0), 
                           cantidad_minima: Decimal = Decimal(0), precio_compra: Decimal = Decimal(0),
                           descripcion: Optional[str] = None):
    """
    Busca un insumo por nombre normalizado, si no existe lo crea.
    Retorna el id_insumo y si fue creado o no.
    """
    insumo_existente = buscar_insumo_por_nombre(nombre)
    if insumo_existente:
        return insumo_existente["id_insumo"], False
    
    # Crear nuevo insumo
    nuevo_insumo = InsumoCreate(
        nombre=nombre,
        unidad_medida=unidad_medida,
        cantidad_actual=cantidad_actual,
        cantidad_minima=cantidad_minima,
        precio_compra=precio_compra,
        descripcion=descripcion
    )
    resultado = crear_insumo(nuevo_insumo)
    
    if "error" in resultado:
        raise Exception(resultado["error"])
    
    return resultado["id_insumo"], True

def ver_todos_insumos():
    conexion = conectar()
    if not conexion:
        return {"error": "Error de conexión a la base de datos"}
    
    cursor = conexion.cursor(dictionary=True)
    sql = "SELECT * FROM insumos WHERE activo = 1 ORDER BY nombre"
    cursor.execute(sql)
    filas = cursor.fetchall()
    cursor.close()
    conexion.close()
    return filas

def ver_insumos_normalizados():
    """
    Obtiene todos los insumos activos con nombre y nombre_normalizado
    Útil para crear selects en el frontend
    """
    conexion = conectar()
    if not conexion:
        return {"error": "Error de conexión a la base de datos"}
    
    cursor = conexion.cursor(dictionary=True)
    sql = """
    SELECT id_insumo, nombre, nombre_normalizado, unidad_medida, cantidad_actual
    FROM insumos 
    WHERE activo = 1 
    ORDER BY nombre
    """
    cursor.execute(sql)
    filas = cursor.fetchall()
    cursor.close()
    conexion.close()
    return filas

def ver_insumo_by_id(id_insumo: int):
    conexion = conectar()
    if not conexion:
        return {"error": "Error de conexión a la base de datos"}
    
    cursor = conexion.cursor(dictionary=True)
    sql = "SELECT * FROM insumos WHERE id_insumo = %s"
    cursor.execute(sql, (id_insumo,))
    insumo = cursor.fetchone()
    cursor.close()
    conexion.close()
    
    if not insumo:
        return {"error": "Insumo no encontrado"}
    return insumo

def editar_insumo(id_insumo: int, insumo: InsumoUpdate):
    conexion = conectar()
    if not conexion:
        return {"error": "Error de conexión a la base de datos"}
    
    cursor = conexion.cursor()
    campos = []
    valores = []
    
    if insumo.nombre is not None:
        # Si se actualiza el nombre, también actualizar nombre_normalizado
        nombre_normalizado = normalizar_nombre(insumo.nombre)
        # Verificar si ya existe otro insumo con el mismo nombre normalizado
        sql_check = "SELECT id_insumo FROM insumos WHERE nombre_normalizado = %s AND id_insumo != %s"
        cursor.execute(sql_check, (nombre_normalizado, id_insumo))
        if cursor.fetchone():
            cursor.close()
            conexion.close()
            return {"error": "Ya existe un insumo con ese nombre"}
        
        campos.append("nombre = %s")
        valores.append(insumo.nombre)
        campos.append("nombre_normalizado = %s")
        valores.append(nombre_normalizado)
    if insumo.descripcion is not None:
        campos.append("descripcion = %s")
        valores.append(insumo.descripcion)
    if insumo.unidad_medida is not None:
        campos.append("unidad_medida = %s")
        valores.append(insumo.unidad_medida)
    if insumo.cantidad_actual is not None:
        campos.append("cantidad_actual = %s")
        valores.append(insumo.cantidad_actual)
    if insumo.cantidad_minima is not None:
        campos.append("cantidad_minima = %s")
        valores.append(insumo.cantidad_minima)
    if insumo.precio_compra is not None:
        campos.append("precio_compra = %s")
        valores.append(insumo.precio_compra)
    if insumo.activo is not None:
        campos.append("activo = %s")
        valores.append(insumo.activo)
    
    if not campos:
        cursor.close()
        conexion.close()
        return {"error": "No hay campos para actualizar"}
    
    valores.append(id_insumo)
    sql = f"UPDATE insumos SET {', '.join(campos)} WHERE id_insumo = %s"
    
    try:
        cursor.execute(sql, valores)
        conexion.commit()
        if cursor.rowcount == 0:
            cursor.close()
            conexion.close()
            return {"error": "Insumo no encontrado"}
        cursor.close()
        conexion.close()
        return {"message": "Insumo actualizado correctamente"}
    except Exception as e:
        conexion.rollback()
        cursor.close()
        conexion.close()
        return {"error": f"Error al actualizar insumo: {str(e)}"}

def restar_insumo(id_insumo: int, cantidad: float):
    """Resta cantidad del inventario"""
    conexion = conectar()
    if not conexion:
        return {"error": "Error de conexión a la base de datos"}
    
    cursor = conexion.cursor(dictionary=True)
    
    # Verificar cantidad actual
    sql_check = "SELECT cantidad_actual FROM insumos WHERE id_insumo = %s"
    cursor.execute(sql_check, (id_insumo,))
    insumo = cursor.fetchone()
    
    if not insumo:
        cursor.close()
        conexion.close()
        return {"error": "Insumo no encontrado"}
    
    nueva_cantidad = float(insumo["cantidad_actual"]) - cantidad
    
    if nueva_cantidad < 0:
        cursor.close()
        conexion.close()
        return {"error": "No hay suficiente inventario"}
    
    # Actualizar cantidad
    sql_update = "UPDATE insumos SET cantidad_actual = %s WHERE id_insumo = %s"
    try:
        cursor.execute(sql_update, (nueva_cantidad, id_insumo))
        conexion.commit()
        cursor.close()
        conexion.close()
        return {"message": "Inventario actualizado correctamente", "cantidad_restante": nueva_cantidad}
    except Exception as e:
        conexion.rollback()
        cursor.close()
        conexion.close()
        return {"error": f"Error al actualizar inventario: {str(e)}"}

def registrar_movimiento(movimiento: MovimientoInventarioCreate):
    """Registra un movimiento en el inventario"""
    conexion = conectar()
    if not conexion:
        return {"error": "Error de conexión a la base de datos"}
    
    cursor = conexion.cursor()
    
    # Actualizar cantidad del insumo
    if movimiento.tipo_movimiento == "entrada":
        sql_update = "UPDATE insumos SET cantidad_actual = cantidad_actual + %s WHERE id_insumo = %s"
    else:  # salida
        sql_update = "UPDATE insumos SET cantidad_actual = cantidad_actual - %s WHERE id_insumo = %s"
    
    try:
        cursor.execute(sql_update, (movimiento.cantidad, movimiento.id_insumo))
        
        # Registrar movimiento
        sql_mov = """
        INSERT INTO movimientos_inventario(
            id_insumo, tipo_movimiento, cantidad, motivo, observaciones, fecha_movimiento
        )
        VALUES (%s, %s, %s, %s, %s, %s)
        """
        datos_mov = (
            movimiento.id_insumo, movimiento.tipo_movimiento, movimiento.cantidad,
            movimiento.motivo, movimiento.observaciones, datetime.now()
        )
        cursor.execute(sql_mov, datos_mov)
        
        conexion.commit()
        movimiento_id = cursor.lastrowid
        cursor.close()
        conexion.close()
        return {"message": "Movimiento registrado correctamente", "id_movimiento": movimiento_id}
    except Exception as e:
        conexion.rollback()
        cursor.close()
        conexion.close()
        return {"error": f"Error al registrar movimiento: {str(e)}"}

def obtener_insumos_bajo_stock():
    """Obtiene insumos con stock por debajo del mínimo"""
    conexion = conectar()
    if not conexion:
        return {"error": "Error de conexión a la base de datos"}
    
    cursor = conexion.cursor(dictionary=True)
    sql = """
    SELECT * FROM insumos 
    WHERE cantidad_actual <= cantidad_minima AND activo = 1
    """
    cursor.execute(sql)
    filas = cursor.fetchall()
    cursor.close()
    conexion.close()
    return filas

