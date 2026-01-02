from database.conexion import conectar
from schemas.preorden_schema import PreordenCreate, PreordenUpdate, EstadoPreordenEnum
from datetime import datetime
from decimal import Decimal
import uuid

def generar_ticket_id():
    """Genera un ID de ticket único"""
    # Formato: TICKET-YYYYMMDD-HHMMSS-XXXX (últimos 4 caracteres aleatorios)
    timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    random_suffix = str(uuid.uuid4())[:4].upper().replace('-', '')
    return f"TICKET-{timestamp}-{random_suffix}"

def obtener_id_usuario_ventas_globales(cursor_existente=None):
    """Obtiene el ID del usuario 'Ventas Globales' para usar por defecto
    
    Args:
        cursor_existente: Si se proporciona, usa este cursor en lugar de crear uno nuevo
    """
    if cursor_existente:
        # Usar el cursor existente
        try:
            cursor_existente.execute("SELECT id_usuario FROM usuarios WHERE correo = %s", ("ventas@globales.com",))
            usuario = cursor_existente.fetchone()
            if usuario:
                return usuario['id_usuario']
            return None
        except Exception as e:
            print(f"Error al obtener usuario Ventas Globales: {e}")
            return None
    else:
        # Crear nueva conexión
        conexion = conectar()
        if not conexion:
            return None
        
        cursor = conexion.cursor(dictionary=True)
        
        try:
            cursor.execute("SELECT id_usuario FROM usuarios WHERE correo = %s", ("ventas@globales.com",))
            usuario = cursor.fetchone()
            
            if usuario:
                return usuario['id_usuario']
            return None
        except Exception as e:
            print(f"Error al obtener usuario Ventas Globales: {e}")
            return None
        finally:
            cursor.close()
            conexion.close()

def crear_preorden(preorden: PreordenCreate):
    """Crea una pre-orden desde la página web (público)"""
    conexion = conectar()
    if not conexion:
        return {"error": "Error de conexión a la base de datos"}
    
    cursor = conexion.cursor()
    
    try:
        # Calcular el total de la pre-orden
        total = Decimal(0)
        for detalle in preorden.detalles:
            # Obtener precio del producto
            sql_precio = "SELECT precio FROM productos WHERE id_producto = %s AND activo = 1"
            cursor.execute(sql_precio, (detalle.id_producto,))
            producto = cursor.fetchone()
            if not producto:
                cursor.close()
                conexion.close()
                return {"error": f"Producto {detalle.id_producto} no encontrado o inactivo"}
            total += Decimal(str(producto[0])) * detalle.cantidad
        
        # Sumar extra por leche deslactosada si existe
        extra_leche = preorden.extra_leche if preorden.extra_leche is not None else Decimal(0)
        total_final = total + extra_leche
        
        # Crear la pre-orden (origen='web' para pedidos públicos)
        sql_preorden = """
        INSERT INTO preordenes(nombre_cliente, estado, total, tipo_servicio, comentarios, tipo_leche, extra_leche, origen, fecha_creacion)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        datos_preorden = (
            preorden.nombre_cliente,
            EstadoPreordenEnum.PREORDEN.value,
            total_final,
            preorden.tipo_servicio,
            preorden.comentarios,
            preorden.tipo_leche,
            extra_leche,
            'web',  # Origen: web (pedido público)
            datetime.now()
        )
        cursor.execute(sql_preorden, datos_preorden)
        preorden_id = cursor.lastrowid
        
        # Crear los detalles
        sql_detalle = """
        INSERT INTO detalles_preorden(id_preorden, id_producto, cantidad, observaciones)
        VALUES (%s, %s, %s, %s)
        """
        for detalle in preorden.detalles:
            datos_detalle = (
                preorden_id, detalle.id_producto, detalle.cantidad, detalle.observaciones
            )
            cursor.execute(sql_detalle, datos_detalle)
        
        conexion.commit()
        cursor.close()
        conexion.close()
        return {"message": "Pre-orden creada correctamente", "id_preorden": preorden_id, "total": float(total_final)}
    except Exception as e:
        conexion.rollback()
        cursor.close()
        conexion.close()
        return {"error": f"Error al crear pre-orden: {str(e)}"}

def ver_preorden_by_id(id_preorden: int):
    """Obtiene una pre-orden específica"""
    conexion = conectar()
    if not conexion:
        return {"error": "Error de conexión a la base de datos"}
    
    cursor = conexion.cursor(dictionary=True)
    
    sql_preorden = "SELECT * FROM preordenes WHERE id_preorden = %s"
    cursor.execute(sql_preorden, (id_preorden,))
    preorden = cursor.fetchone()
    
    if not preorden:
        cursor.close()
        conexion.close()
        return {"error": "Pre-orden no encontrada"}
    
    # Obtener detalles
    sql_detalles = """
    SELECT dp.*, p.nombre as producto_nombre, p.precio
    FROM detalles_preorden dp
    JOIN productos p ON dp.id_producto = p.id_producto
    WHERE dp.id_preorden = %s
    """
    cursor.execute(sql_detalles, (id_preorden,))
    detalles = cursor.fetchall()
    
    preorden["detalles"] = detalles
    cursor.close()
    conexion.close()
    return preorden

def ver_preordenes_por_estado(estado: EstadoPreordenEnum, origen: str = None):
    """Obtiene pre-órdenes filtradas por estado y opcionalmente por origen"""
    conexion = conectar()
    if not conexion:
        return {"error": "Error de conexión a la base de datos"}
    
    cursor = conexion.cursor(dictionary=True)
    
    if origen:
        sql = """
        SELECT * FROM preordenes 
        WHERE estado = %s AND origen = %s
        ORDER BY fecha_creacion ASC
        """
        cursor.execute(sql, (estado.value, origen))
    else:
        sql = """
        SELECT * FROM preordenes 
        WHERE estado = %s 
        ORDER BY fecha_creacion ASC
        """
        cursor.execute(sql, (estado.value,))
    
    preordenes = cursor.fetchall()
    
    # Obtener detalles para cada pre-orden
    for preorden in preordenes:
        sql_detalles = """
        SELECT dp.*, p.nombre as producto_nombre, p.precio
        FROM detalles_preorden dp
        JOIN productos p ON dp.id_producto = p.id_producto
        WHERE dp.id_preorden = %s
        """
        cursor.execute(sql_detalles, (preorden["id_preorden"],))
        preorden["detalles"] = cursor.fetchall()
    
    cursor.close()
    conexion.close()
    return preordenes

def ver_preordenes_pendientes():
    """Obtiene pre-órdenes pendientes (preorden y en_caja) - para pantalla de caja"""
    conexion = conectar()
    if not conexion:
        return {"error": "Error de conexión a la base de datos"}
    
    cursor = conexion.cursor(dictionary=True)
    sql = """
    SELECT * FROM preordenes 
    WHERE estado IN ('preorden', 'en_caja')
    ORDER BY fecha_creacion ASC
    """
    cursor.execute(sql)
    preordenes = cursor.fetchall()
    
    # Obtener detalles para cada pre-orden
    for preorden in preordenes:
        sql_detalles = """
        SELECT dp.*, p.nombre as producto_nombre, p.precio
        FROM detalles_preorden dp
        JOIN productos p ON dp.id_producto = p.id_producto
        WHERE dp.id_preorden = %s
        """
        cursor.execute(sql_detalles, (preorden["id_preorden"],))
        preorden["detalles"] = cursor.fetchall()
    
    cursor.close()
    conexion.close()
    return preordenes

def actualizar_preorden(id_preorden: int, preorden: PreordenUpdate):
    """Actualiza una pre-orden (usado por cajero)"""
    conexion = conectar()
    if not conexion:
        return {"error": "Error de conexión a la base de datos"}
    
    cursor = conexion.cursor()
    
    campos = []
    valores = []
    
    if preorden.nombre_cliente is not None:
        campos.append("nombre_cliente = %s")
        valores.append(preorden.nombre_cliente)
    
    if preorden.estado is not None:
        campos.append("estado = %s")
        valores.append(preorden.estado.value)
        campos.append("fecha_actualizacion = %s")
        valores.append(datetime.now())
    
    if not campos:
        cursor.close()
        conexion.close()
        return {"error": "No hay campos para actualizar"}
    
    valores.append(id_preorden)
    sql = f"UPDATE preordenes SET {', '.join(campos)} WHERE id_preorden = %s"
    
    try:
        cursor.execute(sql, valores)
        conexion.commit()
        if cursor.rowcount == 0:
            cursor.close()
            conexion.close()
            return {"error": "Pre-orden no encontrada"}
        cursor.close()
        conexion.close()
        return {"message": "Pre-orden actualizada correctamente"}
    except Exception as e:
        conexion.rollback()
        cursor.close()
        conexion.close()
        return {"error": f"Error al actualizar pre-orden: {str(e)}"}

def procesar_pago_preorden(id_preorden: int, id_usuario: int, metodo_pago: str, id_cliente: int = None):
    """
    Procesa el pago de una pre-orden:
    1. Valida usuario, pre-orden y detalles
    2. Valida productos y calcula totales
    3. Crea la venta y detalles de venta
    4. Crea la comanda y detalles de comanda
    5. Actualiza el estado de la pre-orden a 'pagada'
    
    Todo dentro de una transacción única para garantizar consistencia.
    Si id_usuario es None o no existe, usa el usuario 'Ventas Globales' por defecto
    """
    conexion = conectar()
    if not conexion:
        return {"error": "Error de conexión a la base de datos"}
    
    cursor = conexion.cursor(dictionary=True)
    
    try:
        # ========== PASO 1: VALIDAR Y OBTENER USUARIO ==========
        usuario_id_final = id_usuario
        
        if id_usuario:
            cursor.execute("SELECT id_usuario FROM usuarios WHERE id_usuario = %s AND activo = 1", (id_usuario,))
            usuario_existe = cursor.fetchone()
            
            if not usuario_existe:
                usuario_id_final = obtener_id_usuario_ventas_globales(cursor_existente=cursor)
                if not usuario_id_final:
                    cursor.close()
                    conexion.close()
                    return {"error": "No se encontró el usuario 'Ventas Globales'. Ejecuta crear_usuario_ventas_globales.py"}
        else:
            usuario_id_final = obtener_id_usuario_ventas_globales(cursor_existente=cursor)
            if not usuario_id_final:
                cursor.close()
                conexion.close()
                return {"error": "No se encontró el usuario 'Ventas Globales'. Ejecuta crear_usuario_ventas_globales.py"}
        
        # ========== PASO 2: VALIDAR PRE-ORDEN ==========
        cursor.execute("SELECT * FROM preordenes WHERE id_preorden = %s", (id_preorden,))
        preorden = cursor.fetchone()
        
        if not preorden:
            cursor.close()
            conexion.close()
            return {"error": "Pre-orden no encontrada"}
        
        if preorden["estado"] != "en_caja":
            cursor.close()
            conexion.close()
            return {"error": f"La pre-orden debe estar en estado 'en_caja' para procesar el pago. Estado actual: {preorden['estado']}"}
        
        if not preorden.get("total") or preorden["total"] is None or float(preorden["total"]) <= 0:
            cursor.close()
            conexion.close()
            return {"error": "La pre-orden no tiene un total válido"}
        
        # ========== PASO 3: OBTENER Y VALIDAR DETALLES ==========
        cursor.execute("SELECT * FROM detalles_preorden WHERE id_preorden = %s", (id_preorden,))
        detalles = cursor.fetchall()
        
        if not detalles or len(detalles) == 0:
            cursor.close()
            conexion.close()
            return {"error": "La pre-orden no tiene productos"}
        
        # Validar que todos los detalles tienen id_producto y cantidad válidos
        for detalle in detalles:
            if not detalle.get("id_producto") or detalle["id_producto"] is None:
                cursor.close()
                conexion.close()
                return {"error": f"Detalle de pre-orden sin id_producto válido"}
            if not detalle.get("cantidad") or detalle["cantidad"] <= 0:
                cursor.close()
                conexion.close()
                return {"error": f"Detalle de pre-orden con cantidad inválida: {detalle.get('cantidad')}"}
        
        # ========== PASO 4: VALIDAR PRODUCTOS Y CALCULAR TOTALES ==========
        total_calculado = Decimal(0)
        productos_validados = []
        
        for detalle in detalles:
            id_producto = detalle["id_producto"]
            cantidad = detalle["cantidad"]
            
            # Validar que el producto existe y está activo
            cursor.execute("SELECT precio, activo FROM productos WHERE id_producto = %s", (id_producto,))
            producto_info = cursor.fetchone()
            
            if not producto_info:
                conexion.rollback()
                cursor.close()
                conexion.close()
                return {"error": f"Producto {id_producto} no encontrado"}
            
            if not producto_info.get("activo") or producto_info["activo"] == 0:
                conexion.rollback()
                cursor.close()
                conexion.close()
                return {"error": f"Producto {id_producto} no está activo"}
            
            precio = Decimal(str(producto_info["precio"]))
            subtotal = precio * cantidad
            total_calculado += subtotal
            
            productos_validados.append({
                "id_producto": id_producto,
                "cantidad": cantidad,
                "precio": float(precio),
                "subtotal": float(subtotal),
                "observaciones": detalle.get("observaciones")
            })
        
        # Sumar el extra de leche si existe
        extra_leche = Decimal(str(preorden.get("extra_leche") or 0))
        total_calculado_con_extra = total_calculado + extra_leche
        
        # Validar que el total calculado (con extra) coincida con el total de la pre-orden
        total_preorden = Decimal(str(preorden["total"]))
        diferencia = abs(total_calculado_con_extra - total_preorden)
        
        if diferencia > Decimal("0.01"):  # Permitir diferencia de 1 centavo por redondeo
            cursor.close()
            conexion.close()
            return {
                "error": f"El total calculado (${total_calculado_con_extra}) no coincide con el total de la pre-orden (${total_preorden}). Productos: ${total_calculado}, Extra leche: ${extra_leche}"
            }
        
        # ========== PASO 5: CREAR VENTA (DENTRO DE TRANSACCIÓN) ==========
        # Desactivar autocommit para manejar transacción manualmente
        conexion.autocommit = False
        
        # Obtener información adicional de la pre-orden
        tipo_servicio = preorden.get("tipo_servicio")
        comentarios = preorden.get("comentarios")
        tipo_leche = preorden.get("tipo_leche")
        extra_leche = float(preorden.get("extra_leche") or 0) if preorden.get("extra_leche") else None
        
        sql_venta = """
        INSERT INTO ventas(id_cliente, id_usuario, total, metodo_pago, fecha_venta, tipo_servicio, comentarios, tipo_leche, extra_leche)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        datos_venta = (
            id_cliente if id_cliente else None,
            usuario_id_final,
            float(total_preorden),
            metodo_pago,
            datetime.now(),
            tipo_servicio,
            comentarios,
            tipo_leche,
            extra_leche
        )
        cursor.execute(sql_venta, datos_venta)
        venta_id = cursor.lastrowid
        
        if not venta_id:
            conexion.rollback()
            cursor.close()
            conexion.close()
            return {"error": "No se pudo crear la venta"}
        
        # ========== PASO 6: CREAR DETALLES DE VENTA ==========
        sql_detalle_venta = """
        INSERT INTO detalles_venta(id_venta, id_producto, cantidad, precio_unitario, subtotal)
        VALUES (%s, %s, %s, %s, %s)
        """
        
        for producto in productos_validados:
            datos_detalle = (
                venta_id,
                producto["id_producto"],
                producto["cantidad"],
                producto["precio"],
                producto["subtotal"]
            )
            cursor.execute(sql_detalle_venta, datos_detalle)
        
        # ========== PASO 7: CREAR COMANDA ==========
        sql_comanda = """
        INSERT INTO comandas(id_venta, estado, fecha_creacion)
        VALUES (%s, 'pendiente', %s)
        """
        cursor.execute(sql_comanda, (venta_id, datetime.now()))
        comanda_id = cursor.lastrowid
        
        if not comanda_id:
            conexion.rollback()
            cursor.close()
            conexion.close()
            return {"error": "No se pudo crear la comanda"}
        
        # ========== PASO 8: CREAR DETALLES DE COMANDA ==========
        sql_detalle_comanda = """
        INSERT INTO detalles_comanda(id_comanda, id_producto, cantidad, observaciones)
        VALUES (%s, %s, %s, %s)
        """
        
        for producto in productos_validados:
            datos_detalle_comanda = (
                comanda_id,
                producto["id_producto"],
                producto["cantidad"],
                producto["observaciones"]
            )
            cursor.execute(sql_detalle_comanda, datos_detalle_comanda)
        
        # ========== PASO 9: ACTUALIZAR PRE-ORDEN CON TICKET_ID ==========
        # Generar ticket_id único
        ticket_id = generar_ticket_id()
        
        sql_update = """
        UPDATE preordenes 
        SET estado = 'pagada', id_venta = %s, ticket_id = %s, fecha_actualizacion = %s
        WHERE id_preorden = %s
        """
        cursor.execute(sql_update, (venta_id, ticket_id, datetime.now(), id_preorden))
        
        if cursor.rowcount == 0:
            conexion.rollback()
            cursor.close()
            conexion.close()
            return {"error": "No se pudo actualizar el estado de la pre-orden"}
        
        # ========== PASO 10: COMMIT DE TODA LA TRANSACCIÓN ==========
        conexion.commit()
        
        # Obtener la pre-orden actualizada para retornar el estado y ticket_id
        cursor.execute("SELECT estado, ticket_id FROM preordenes WHERE id_preorden = %s", (id_preorden,))
        preorden_actualizada = cursor.fetchone()
        
        cursor.close()
        conexion.close()
        
        return {
            "message": "Pago procesado correctamente",
            "id_venta": venta_id,
            "id_comanda": comanda_id,
            "id_preorden": id_preorden,
            "ticket_id": preorden_actualizada["ticket_id"] if preorden_actualizada else ticket_id,
            "estado_preorden": preorden_actualizada["estado"] if preorden_actualizada else "pagada",
            "total": float(total_preorden)
        }
        
    except Exception as e:
        # Rollback en caso de cualquier error
        error_msg = str(e)
        try:
            conexion.rollback()
        except:
            pass
        try:
            cursor.close()
        except:
            pass
        try:
            conexion.close()
        except:
            pass
        return {"error": f"Error al procesar pago: {error_msg}"}

def marcar_preorden_en_cocina(id_preorden: int):
    """Marca una pre-orden como en cocina (cuando la comanda está en preparación)"""
    conexion = conectar()
    if not conexion:
        return {"error": "Error de conexión a la base de datos"}
    
    cursor = conexion.cursor()
    sql = """
    UPDATE preordenes 
    SET estado = 'en_cocina', fecha_actualizacion = %s
    WHERE id_preorden = %s AND estado = 'pagada'
    """
    
    try:
        cursor.execute(sql, (datetime.now(), id_preorden))
        conexion.commit()
        if cursor.rowcount == 0:
            cursor.close()
            conexion.close()
            return {"error": "Pre-orden no encontrada o no está en estado 'pagada'"}
        cursor.close()
        conexion.close()
        return {"message": "Pre-orden marcada como en cocina"}
    except Exception as e:
        conexion.rollback()
        cursor.close()
        conexion.close()
        return {"error": f"Error al actualizar estado: {str(e)}"}

def marcar_preorden_lista(id_preorden: int):
    """Marca una pre-orden como lista para entregar"""
    conexion = conectar()
    if not conexion:
        return {"error": "Error de conexión a la base de datos"}
    
    cursor = conexion.cursor()
    sql = """
    UPDATE preordenes 
    SET estado = 'lista', fecha_actualizacion = %s
    WHERE id_preorden = %s AND estado = 'en_cocina'
    """
    
    try:
        cursor.execute(sql, (datetime.now(), id_preorden))
        conexion.commit()
        if cursor.rowcount == 0:
            cursor.close()
            conexion.close()
            return {"error": "Pre-orden no encontrada o no está en estado 'en_cocina'"}
        cursor.close()
        conexion.close()
        return {"message": "Pre-orden marcada como lista"}
    except Exception as e:
        conexion.rollback()
        cursor.close()
        conexion.close()
        return {"error": f"Error al actualizar estado: {str(e)}"}

def marcar_preorden_entregada(id_preorden: int):
    """Marca una pre-orden como entregada"""
    conexion = conectar()
    if not conexion:
        return {"error": "Error de conexión a la base de datos"}
    
    cursor = conexion.cursor()
    sql = """
    UPDATE preordenes 
    SET estado = 'entregada', fecha_actualizacion = %s
    WHERE id_preorden = %s AND estado = 'lista'
    """
    
    try:
        cursor.execute(sql, (datetime.now(), id_preorden))
        conexion.commit()
        if cursor.rowcount == 0:
            cursor.close()
            conexion.close()
            return {"error": "Pre-orden no encontrada o no está en estado 'lista'"}
        cursor.close()
        conexion.close()
        return {"message": "Pre-orden marcada como entregada"}
    except Exception as e:
        conexion.rollback()
        cursor.close()
        conexion.close()
        return {"error": f"Error al actualizar estado: {str(e)}"}


