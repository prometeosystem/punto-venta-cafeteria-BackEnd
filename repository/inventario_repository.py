from database.conexion import conectar
from schemas.inventario_schema import InsumoCreate, InsumoUpdate, MovimientoInventarioCreate
from datetime import datetime

def crear_insumo(insumo: InsumoCreate):
    conexion = conectar()
    if not conexion:
        return {"error": "Error de conexión a la base de datos"}
    
    cursor = conexion.cursor()
    sql = """
    INSERT INTO insumos(
        nombre, descripcion, unidad_medida, cantidad_actual,
        cantidad_minima, precio_compra, activo
    )
    VALUES (%s, %s, %s, %s, %s, %s, %s)
    """
    datos = (
        insumo.nombre, insumo.descripcion, insumo.unidad_medida,
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

def ver_todos_insumos():
    conexion = conectar()
    if not conexion:
        return {"error": "Error de conexión a la base de datos"}
    
    cursor = conexion.cursor(dictionary=True)
    sql = "SELECT * FROM insumos WHERE activo = 1"
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
        campos.append("nombre = %s")
        valores.append(insumo.nombre)
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

