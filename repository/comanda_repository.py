from database.conexion import conectar
from schemas.comanda_schema import ComandaCreate, ComandaUpdate, EstadoComandaEnum
from datetime import datetime

def obtener_info_pedido_para_comanda(cursor, id_venta):
    """
    Obtiene información completa del pedido (pre-orden o venta) para una comanda.
    Primero busca en pre-órdenes, si no existe, busca en ventas.
    Incluye: origen, ticket_id, nombre_cliente, tipo_servicio, tipo_leche, extra_leche, comentarios
    """
    # Buscar en pre-órdenes primero (incluye tanto web como sistema)
    sql_preorden = """
    SELECT 
        id_preorden, 
        origen,
        ticket_id,
        nombre_cliente, 
        tipo_servicio, 
        comentarios, 
        tipo_leche, 
        extra_leche
    FROM preordenes
    WHERE id_venta = %s
    """
    cursor.execute(sql_preorden, (id_venta,))
    preorden = cursor.fetchone()
    
    if preorden:
        return preorden
    
    # Si no hay pre-orden, buscar en ventas (para compatibilidad con ventas antiguas)
    sql_venta = """
    SELECT tipo_servicio, comentarios, tipo_leche, extra_leche
    FROM ventas
    WHERE id_venta = %s
    """
    cursor.execute(sql_venta, (id_venta,))
    venta_info = cursor.fetchone()
    
    if venta_info and (venta_info.get("tipo_servicio") or venta_info.get("tipo_leche") or venta_info.get("comentarios")):
        # Crear estructura similar a pre-orden para consistencia
        return {
            "id_preorden": None,
            "origen": "sistema",  # Asumir sistema si viene de ventas
            "ticket_id": None,
            "nombre_cliente": None,
            "tipo_servicio": venta_info.get("tipo_servicio"),
            "comentarios": venta_info.get("comentarios"),
            "tipo_leche": venta_info.get("tipo_leche"),
            "extra_leche": venta_info.get("extra_leche")
        }
    
    return None

def crear_comanda(comanda: ComandaCreate):
    conexion = conectar()
    if not conexion:
        return {"error": "Error de conexión a la base de datos"}
    
    cursor = conexion.cursor()
    
    try:
        # Crear la comanda
        sql_comanda = """
        INSERT INTO comandas(id_venta, estado, fecha_creacion)
        VALUES (%s, %s, %s)
        """
        datos_comanda = (comanda.id_venta, comanda.estado.value, datetime.now())
        cursor.execute(sql_comanda, datos_comanda)
        comanda_id = cursor.lastrowid
        
        # Crear los detalles de la comanda
        sql_detalle = """
        INSERT INTO detalles_comanda(id_comanda, id_producto, cantidad, observaciones)
        VALUES (%s, %s, %s, %s)
        """
        for detalle in comanda.detalles:
            datos_detalle = (
                comanda_id, detalle.id_producto, detalle.cantidad, detalle.observaciones
            )
            cursor.execute(sql_detalle, datos_detalle)
        
        conexion.commit()
        cursor.close()
        conexion.close()
        return {"message": "Comanda creada correctamente", "id_comanda": comanda_id}
    except Exception as e:
        conexion.rollback()
        cursor.close()
        conexion.close()
        return {"error": f"Error al crear comanda: {str(e)}"}

def ver_comanda_by_id(id_comanda: int):
    conexion = conectar()
    if not conexion:
        return {"error": "Error de conexión a la base de datos"}
    
    cursor = conexion.cursor(dictionary=True)
    
    # Obtener la comanda
    sql_comanda = "SELECT * FROM comandas WHERE id_comanda = %s"
    cursor.execute(sql_comanda, (id_comanda,))
    comanda = cursor.fetchone()
    
    if not comanda:
        cursor.close()
        conexion.close()
        return {"error": "Comanda no encontrada"}
    
    # Obtener los detalles
    sql_detalles = """
    SELECT dc.*, p.nombre as producto_nombre
    FROM detalles_comanda dc
    JOIN productos p ON dc.id_producto = p.id_producto
    WHERE dc.id_comanda = %s
    """
    cursor.execute(sql_detalles, (id_comanda,))
    detalles = cursor.fetchall()
    
    comanda["detalles"] = detalles
    
    # Obtener información del pedido (pre-orden o venta)
    info_pedido = obtener_info_pedido_para_comanda(cursor, comanda["id_venta"])
    comanda["preorden"] = info_pedido
    
    cursor.close()
    conexion.close()
    return comanda

def ver_comandas_por_estado(estado: EstadoComandaEnum):
    conexion = conectar()
    if not conexion:
        return {"error": "Error de conexión a la base de datos"}
    
    cursor = conexion.cursor(dictionary=True)
    sql = """
    SELECT c.*, v.total, v.fecha_venta
    FROM comandas c
    JOIN ventas v ON c.id_venta = v.id_venta
    WHERE c.estado = %s
    ORDER BY c.fecha_creacion ASC
    """
    cursor.execute(sql, (estado.value,))
    comandas = cursor.fetchall()
    
    # Obtener detalles y información de pre-orden para cada comanda
    for comanda in comandas:
        # Obtener detalles de la comanda
        sql_detalles = """
        SELECT dc.*, p.nombre as producto_nombre
        FROM detalles_comanda dc
        JOIN productos p ON dc.id_producto = p.id_producto
        WHERE dc.id_comanda = %s
        """
        cursor.execute(sql_detalles, (comanda["id_comanda"],))
        comanda["detalles"] = cursor.fetchall()
        
        # Obtener información del pedido (pre-orden o venta)
        info_pedido = obtener_info_pedido_para_comanda(cursor, comanda["id_venta"])
        comanda["preorden"] = info_pedido
    
    cursor.close()
    conexion.close()
    return comandas

def actualizar_estado_comanda(id_comanda: int, estado: EstadoComandaEnum):
    """Actualiza el estado de una comanda y resta insumos si está terminada"""
    conexion = conectar()
    if not conexion:
        return {"error": "Error de conexión a la base de datos"}
    
    cursor = conexion.cursor(dictionary=True)
    
    try:
        # Verificar que la comanda existe y obtener id_venta
        sql_check = "SELECT estado, id_venta FROM comandas WHERE id_comanda = %s"
        cursor.execute(sql_check, (id_comanda,))
        comanda_actual = cursor.fetchone()
        
        if not comanda_actual:
            cursor.close()
            conexion.close()
            return {"error": "Comanda no encontrada"}
        
        id_venta = comanda_actual["id_venta"]
        
        # Si se marca como terminada, restar insumos
        if estado == EstadoComandaEnum.TERMINADA and comanda_actual["estado"] != "terminada":
            # Obtener detalles de la comanda
            sql_detalles = "SELECT id_producto, cantidad FROM detalles_comanda WHERE id_comanda = %s"
            cursor.execute(sql_detalles, (id_comanda,))
            detalles = cursor.fetchall()
            
            # Para cada producto, obtener sus insumos de la receta y restar
            for detalle in detalles:
                sql_receta = """
                SELECT id_insumo, cantidad_necesaria
                FROM recetas_insumos
                WHERE id_producto = %s
                """
                cursor.execute(sql_receta, (detalle["id_producto"],))
                receta = cursor.fetchall()
                
                # Restar cada insumo según la cantidad del producto
                for insumo_receta in receta:
                    cantidad_a_restar = float(insumo_receta["cantidad_necesaria"]) * detalle["cantidad"]
                    
                    # Verificar stock disponible
                    sql_stock = "SELECT cantidad_actual FROM insumos WHERE id_insumo = %s"
                    cursor.execute(sql_stock, (insumo_receta["id_insumo"],))
                    stock = cursor.fetchone()
                    
                    if stock and float(stock["cantidad_actual"]) >= cantidad_a_restar:
                        # Restar del inventario
                        sql_update = """
                        UPDATE insumos 
                        SET cantidad_actual = cantidad_actual - %s 
                        WHERE id_insumo = %s
                        """
                        cursor.execute(sql_update, (cantidad_a_restar, insumo_receta["id_insumo"]))
                        
                        # Registrar movimiento
                        sql_mov = """
                        INSERT INTO movimientos_inventario(
                            id_insumo, tipo_movimiento, cantidad, motivo, fecha_movimiento
                        )
                        VALUES (%s, 'salida', %s, 'Comanda terminada', %s)
                        """
                        cursor.execute(sql_mov, (
                            insumo_receta["id_insumo"],
                            cantidad_a_restar,
                            datetime.now()
                        ))
                    else:
                        conexion.rollback()
                        cursor.close()
                        conexion.close()
                        return {
                            "error": f"Insumo {insumo_receta['id_insumo']} sin stock suficiente"
                        }
        
        # Actualizar estado de la comanda
        sql_update = """
        UPDATE comandas 
        SET estado = %s, fecha_actualizacion = %s 
        WHERE id_comanda = %s
        """
        cursor.execute(sql_update, (estado.value, datetime.now(), id_comanda))
        
        # Sincronizar estado de pre-orden si existe
        if id_venta:
            # Buscar pre-orden asociada a esta venta
            sql_preorden = "SELECT id_preorden FROM preordenes WHERE id_venta = %s"
            cursor.execute(sql_preorden, (id_venta,))
            preorden = cursor.fetchone()
            
            if preorden:
                # Si la comanda pasa a "en_preparacion", la pre-orden pasa a "en_cocina"
                if estado == EstadoComandaEnum.EN_PREPARACION:
                    sql_update_preorden = """
                    UPDATE preordenes 
                    SET estado = 'en_cocina', fecha_actualizacion = %s 
                    WHERE id_preorden = %s
                    """
                    cursor.execute(sql_update_preorden, (datetime.now(), preorden["id_preorden"]))
                # Si la comanda pasa a "terminada", la pre-orden pasa a "lista"
                elif estado == EstadoComandaEnum.TERMINADA:
                    sql_update_preorden = """
                    UPDATE preordenes 
                    SET estado = 'lista', fecha_actualizacion = %s 
                    WHERE id_preorden = %s
                    """
                    cursor.execute(sql_update_preorden, (datetime.now(), preorden["id_preorden"]))
        
        conexion.commit()
        cursor.close()
        conexion.close()
        return {"message": "Estado de comanda actualizado correctamente"}
    except Exception as e:
        conexion.rollback()
        cursor.close()
        conexion.close()
        return {"error": f"Error al actualizar comanda: {str(e)}"}

def ver_todas_comandas():
    conexion = conectar()
    if not conexion:
        return {"error": "Error de conexión a la base de datos"}
    
    cursor = conexion.cursor(dictionary=True)
    sql = """
    SELECT c.*, v.total, v.fecha_venta
    FROM comandas c
    JOIN ventas v ON c.id_venta = v.id_venta
    ORDER BY c.fecha_creacion DESC
    """
    cursor.execute(sql)
    comandas = cursor.fetchall()
    
    for comanda in comandas:
        # Obtener detalles de la comanda
        sql_detalles = """
        SELECT dc.*, p.nombre as producto_nombre
        FROM detalles_comanda dc
        JOIN productos p ON dc.id_producto = p.id_producto
        WHERE dc.id_comanda = %s
        """
        cursor.execute(sql_detalles, (comanda["id_comanda"],))
        comanda["detalles"] = cursor.fetchall()
        
        # Obtener información del pedido (pre-orden o venta)
        info_pedido = obtener_info_pedido_para_comanda(cursor, comanda["id_venta"])
        comanda["preorden"] = info_pedido
    
    cursor.close()
    conexion.close()
    return comandas

