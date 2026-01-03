from database.conexion import conectar
from schemas.comanda_schema import ComandaCreate, ComandaUpdate, EstadoComandaEnum
from datetime import datetime
from decimal import Decimal
from utils.conversiones import convertir_unidades, son_unidades_compatibles

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
    
    cursor = conexion.cursor(dictionary=True)
    
    try:
        # ⚠️ IMPORTANTE: Verificar si ya existe una comanda para esta venta
        cursor.execute("SELECT id_comanda FROM comandas WHERE id_venta = %s", (comanda.id_venta,))
        comanda_existente = cursor.fetchone()
        
        if comanda_existente:
            cursor.close()
            conexion.close()
            return {
                "error": f"Ya existe una comanda (ID: {comanda_existente['id_comanda']}) para la venta {comanda.id_venta}. No se puede crear otra.",
                "id_comanda_existente": comanda_existente['id_comanda']
            }
        
        # Si no existe, crear la comanda
        cursor_normal = conexion.cursor()
        sql_comanda = """
        INSERT INTO comandas(id_venta, estado, fecha_creacion)
        VALUES (%s, %s, %s)
        """
        datos_comanda = (comanda.id_venta, comanda.estado.value, datetime.now())
        cursor_normal.execute(sql_comanda, datos_comanda)
        comanda_id = cursor_normal.lastrowid
        
        # Crear los detalles de la comanda
        sql_detalle = """
        INSERT INTO detalles_comanda(id_comanda, id_producto, cantidad, observaciones)
        VALUES (%s, %s, %s, %s)
        """
        for detalle in comanda.detalles:
            datos_detalle = (
                comanda_id, detalle.id_producto, detalle.cantidad, detalle.observaciones
            )
            cursor_normal.execute(sql_detalle, datos_detalle)
        
        conexion.commit()
        cursor.close()
        cursor_normal.close()
        conexion.close()
        return {"message": "Comanda creada correctamente", "id_comanda": comanda_id}
    except Exception as e:
        conexion.rollback()
        cursor.close()
        if 'cursor_normal' in locals():
            cursor_normal.close()
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
        
        # Variables para tracking de insumos restados
        insumos_restados = []
        errores_insumos = []
        
        # Si se marca como terminada, restar insumos
        # Verificar que el estado anterior no sea "terminada" para evitar restar dos veces
        estado_anterior = comanda_actual["estado"]
        estado_terminada_value = EstadoComandaEnum.TERMINADA.value  # "terminada"
        
        # Verificar condiciones (guardar para usar después)
        es_terminada = (estado == EstadoComandaEnum.TERMINADA or (hasattr(estado, 'value') and estado.value == "terminada"))
        no_estaba_terminada = (estado_anterior != "terminada" and estado_anterior != estado_terminada_value)
        
        if es_terminada and no_estaba_terminada:
            # Verificar si existe unidad_medida en recetas (una sola vez, fuera del loop)
            cursor.execute("""
                SELECT COUNT(*) as existe 
                FROM INFORMATION_SCHEMA.COLUMNS 
                WHERE TABLE_SCHEMA = DATABASE() 
                AND TABLE_NAME = 'recetas_insumos' 
                AND COLUMN_NAME = 'unidad_medida'
            """)
            tiene_unidad_medida = cursor.fetchone()['existe'] > 0
            
            # Obtener detalles de la comanda
            sql_detalles = "SELECT id_producto, cantidad FROM detalles_comanda WHERE id_comanda = %s"
            cursor.execute(sql_detalles, (id_comanda,))
            detalles = cursor.fetchall()
            
            if not detalles:
                # No hay detalles, continuar sin error
                pass
            else:
                # Para cada producto, obtener sus insumos de la receta y restar
                for detalle in detalles:
                    # Obtener recetas del producto
                    if tiene_unidad_medida:
                        sql_receta = """
                        SELECT id_insumo, cantidad_necesaria, unidad_medida
                        FROM recetas_insumos
                        WHERE id_producto = %s
                        """
                    else:
                        sql_receta = """
                        SELECT id_insumo, cantidad_necesaria
                        FROM recetas_insumos
                        WHERE id_producto = %s
                        """
                    
                    cursor.execute(sql_receta, (detalle["id_producto"],))
                    receta = cursor.fetchall()
                    
                    if not receta:
                        # Producto sin recetas, registrar advertencia
                        errores_insumos.append(f"Producto ID {detalle['id_producto']} no tiene recetas (insumos) configuradas")
                        continue
                    
                    # Restar cada insumo según la cantidad del producto
                    for insumo_receta in receta:
                        try:
                            cantidad_necesaria = Decimal(str(insumo_receta["cantidad_necesaria"]))
                            cantidad_total = cantidad_necesaria * Decimal(str(detalle["cantidad"]))
                            
                            # Obtener unidad de medida de la receta y del insumo
                            unidad_receta = insumo_receta.get("unidad_medida", None) if tiene_unidad_medida else None
                            
                            # Obtener información del insumo (cantidad y unidad)
                            sql_insumo = "SELECT cantidad_actual, unidad_medida FROM insumos WHERE id_insumo = %s"
                            cursor.execute(sql_insumo, (insumo_receta["id_insumo"],))
                            insumo_info = cursor.fetchone()
                            
                            if not insumo_info:
                                errores_insumos.append(f"Insumo ID {insumo_receta['id_insumo']} no encontrado")
                                continue
                            
                            unidad_insumo = insumo_info["unidad_medida"]
                            cantidad_actual_insumo = Decimal(str(insumo_info["cantidad_actual"]))
                            
                            # Si hay unidad en la receta, convertir; si no, usar la del insumo
                            if unidad_receta and unidad_receta != unidad_insumo:
                                # Verificar compatibilidad
                                if son_unidades_compatibles(unidad_receta, unidad_insumo):
                                    # Convertir cantidad de la receta a la unidad del insumo
                                    cantidad_a_restar = convertir_unidades(
                                        cantidad_total,
                                        unidad_receta,
                                        unidad_insumo
                                    )
                                else:
                                    # Unidades incompatibles
                                    errores_insumos.append(f"Insumo ID {insumo_receta['id_insumo']}: unidades incompatibles ({unidad_receta} vs {unidad_insumo})")
                                    continue
                            else:
                                # Misma unidad o no hay unidad en receta
                                cantidad_a_restar = cantidad_total
                            
                            # Verificar stock disponible
                            if cantidad_actual_insumo >= cantidad_a_restar:
                                # Restar del inventario
                                # ⚠️ Usar Decimal directamente para mantener precisión
                                sql_update = """
                                UPDATE insumos 
                                SET cantidad_actual = cantidad_actual - %s 
                                WHERE id_insumo = %s
                                """
                                # Convertir Decimal a float solo para la consulta SQL (MySQL requiere float para DECIMAL)
                                cantidad_a_restar_float = float(cantidad_a_restar)
                                cursor.execute(sql_update, (cantidad_a_restar_float, insumo_receta["id_insumo"]))
                                
                                # Registrar movimiento
                                sql_mov = """
                                INSERT INTO movimientos_inventario(
                                    id_insumo, tipo_movimiento, cantidad, motivo, fecha_movimiento
                                )
                                VALUES (%s, 'salida', %s, 'Comanda terminada', %s)
                                """
                                cursor.execute(sql_mov, (
                                    insumo_receta["id_insumo"],
                                    cantidad_a_restar_float,
                                    datetime.now()
                                ))
                                
                                insumos_restados.append({
                                    "id_insumo": insumo_receta["id_insumo"],
                                    "cantidad_restada": float(cantidad_a_restar),
                                    "unidad": unidad_insumo,
                                    "cantidad_original_receta": float(cantidad_necesaria),
                                    "unidad_original_receta": unidad_receta or unidad_insumo,
                                    "cantidad_productos": int(detalle["cantidad"])
                                })
                            else:
                                # Stock insuficiente
                                errores_insumos.append(f"Insumo ID {insumo_receta['id_insumo']}: stock insuficiente (tiene {cantidad_actual_insumo} {unidad_insumo}, necesita {cantidad_a_restar} {unidad_insumo})")
                        except Exception as e:
                            errores_insumos.append(f"Error al procesar insumo ID {insumo_receta.get('id_insumo', 'desconocido')}: {str(e)}")
                
                # Si hay errores críticos (stock insuficiente), hacer rollback
                if any("stock insuficiente" in error for error in errores_insumos):
                    conexion.rollback()
                    cursor.close()
                    conexion.close()
                    return {
                        "error": "No se pudo completar la operación. Errores:",
                        "errores": errores_insumos
                    }
        
        # Actualizar estado de la comanda
        sql_update = """
        UPDATE comandas 
        SET estado = %s, fecha_actualizacion = %s 
        WHERE id_comanda = %s
        """
        try:
            cursor.execute(sql_update, (estado.value, datetime.now(), id_comanda))
            filas_afectadas = cursor.rowcount
            if filas_afectadas == 0:
                conexion.rollback()
                cursor.close()
                conexion.close()
                return {"error": "No se pudo actualizar el estado de la comanda. La comanda no existe o ya tiene ese estado."}
        except Exception as e:
            conexion.rollback()
            cursor.close()
            conexion.close()
            return {"error": f"Error al actualizar estado de comanda: {str(e)}"}
        
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
        
        try:
            conexion.commit()
            
            # Verificar que el estado se actualizó correctamente
            cursor.execute("SELECT estado FROM comandas WHERE id_comanda = %s", (id_comanda,))
            estado_verificado = cursor.fetchone()
            
            if not estado_verificado:
                cursor.close()
                conexion.close()
                return {"error": "Error: La comanda no existe después de actualizar"}
            
            estado_actual = estado_verificado["estado"]
            
            # Preparar respuesta
            respuesta = {
                "message": "Estado de comanda actualizado correctamente",
                "id_comanda": id_comanda,
                "estado_anterior": estado_anterior,
                "estado_nuevo": estado_actual,
                "actualizado": True
            }
            
            # Si se marcó como terminada, incluir información de insumos restados
            if es_terminada and no_estaba_terminada:
                if insumos_restados:
                    respuesta["insumos_restados"] = insumos_restados
                    respuesta["total_insumos_restados"] = len(insumos_restados)
                else:
                    respuesta["advertencia"] = "No se restaron insumos. Verifica que los productos tengan recetas configuradas."
                if errores_insumos:
                    respuesta["errores"] = errores_insumos
            
            cursor.close()
            conexion.close()
            return respuesta
        except Exception as e:
            conexion.rollback()
            cursor.close()
            conexion.close()
            return {"error": f"Error al confirmar cambios en la base de datos: {str(e)}"}
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

