from database.conexion import conectar
from schemas.venta_schema import VentaCreate
from datetime import datetime
from decimal import Decimal
import uuid

def generar_ticket_id():
    """Genera un ID de ticket único"""
    # Formato: TICKET-YYYYMMDD-HHMMSS-XXXX (últimos 4 caracteres aleatorios)
    timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    random_suffix = str(uuid.uuid4())[:4].upper().replace('-', '')
    return f"TICKET-{timestamp}-{random_suffix}"

def crear_venta(venta: VentaCreate):
    conexion = conectar()
    if not conexion:
        return {"error": "Error de conexión a la base de datos"}
    
    cursor = conexion.cursor()
    
    try:
        # Crear la venta
        sql_venta = """
        INSERT INTO ventas(id_cliente, id_usuario, total, metodo_pago, fecha_venta, tipo_servicio, comentarios, tipo_leche, extra_leche)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        datos_venta = (
            venta.id_cliente, venta.id_usuario, venta.total,
            venta.metodo_pago, datetime.now(),
            venta.tipo_servicio, venta.comentarios,
            venta.tipo_leche, float(venta.extra_leche) if venta.extra_leche else None
        )
        cursor.execute(sql_venta, datos_venta)
        venta_id = cursor.lastrowid
        
        if not venta_id:
            conexion.rollback()
            cursor.close()
            conexion.close()
            return {"error": "No se pudo crear la venta"}
        
        # Crear los detalles de la venta
        sql_detalle = """
        INSERT INTO detalles_venta(id_venta, id_producto, cantidad, precio_unitario, subtotal)
        VALUES (%s, %s, %s, %s, %s)
        """
        for detalle in venta.detalles:
            datos_detalle = (
                venta_id, detalle.id_producto, detalle.cantidad,
                detalle.precio_unitario, detalle.subtotal
            )
            cursor.execute(sql_detalle, datos_detalle)
        
        # Crear pedido en preordenes con origen='sistema' y ticket_id
        # Esto unifica pre-órdenes web y órdenes del sistema en la misma tabla
        ticket_id = generar_ticket_id()
        
        # Calcular total de productos (sin incluir extra_leche en detalles)
        total_productos = sum(float(detalle.subtotal) for detalle in venta.detalles)
        extra_leche_valor = float(venta.extra_leche) if venta.extra_leche else 0
        total_pedido = total_productos + extra_leche_valor
        
        sql_pedido = """
        INSERT INTO preordenes(
            nombre_cliente, estado, total, id_venta, ticket_id, origen,
            tipo_servicio, comentarios, tipo_leche, extra_leche, fecha_creacion
        )
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        datos_pedido = (
            None,  # nombre_cliente (se puede obtener del cliente si existe)
            'pagada',  # estado: ya está pagada
            total_pedido,
            venta_id,
            ticket_id,
            'sistema',  # origen: sistema interno
            venta.tipo_servicio,
            venta.comentarios,
            venta.tipo_leche,
            extra_leche_valor if extra_leche_valor > 0 else None,
            datetime.now()
        )
        cursor.execute(sql_pedido, datos_pedido)
        pedido_id = cursor.lastrowid
        
        # Crear detalles del pedido
        sql_detalle_pedido = """
        INSERT INTO detalles_preorden(id_preorden, id_producto, cantidad, observaciones)
        VALUES (%s, %s, %s, %s)
        """
        for detalle in venta.detalles:
            # Obtener observaciones del detalle (puede ser None)
            observaciones = detalle.observaciones if hasattr(detalle, 'observaciones') and detalle.observaciones else None
            datos_detalle_pedido = (
                pedido_id, detalle.id_producto, detalle.cantidad, observaciones
            )
            cursor.execute(sql_detalle_pedido, datos_detalle_pedido)
        
        conexion.commit()
        cursor.close()
        conexion.close()
        return {
            "message": "Venta creada correctamente",
            "id_venta": venta_id,
            "id_pedido": pedido_id,
            "ticket_id": ticket_id
        }
    except Exception as e:
        conexion.rollback()
        cursor.close()
        conexion.close()
        return {"error": f"Error al crear venta: {str(e)}"}

def ver_venta_by_id(id_venta: int):
    conexion = conectar()
    if not conexion:
        return {"error": "Error de conexión a la base de datos"}
    
    cursor = conexion.cursor(dictionary=True)
    
    # Obtener la venta
    sql_venta = "SELECT * FROM ventas WHERE id_venta = %s"
    cursor.execute(sql_venta, (id_venta,))
    venta = cursor.fetchone()
    
    if not venta:
        cursor.close()
        conexion.close()
        return {"error": "Venta no encontrada"}
    
    # Obtener los detalles
    sql_detalles = """
    SELECT * FROM detalles_venta WHERE id_venta = %s
    """
    cursor.execute(sql_detalles, (id_venta,))
    detalles = cursor.fetchall()
    
    venta["detalles"] = detalles
    cursor.close()
    conexion.close()
    return venta

def ver_todas_ventas():
    conexion = conectar()
    if not conexion:
        return {"error": "Error de conexión a la base de datos"}
    
    cursor = conexion.cursor(dictionary=True)
    sql = """
    SELECT v.*, u.nombre as vendedor_nombre, c.nombre as cliente_nombre
    FROM ventas v
    LEFT JOIN usuarios u ON v.id_usuario = u.id_usuario
    LEFT JOIN clientes c ON v.id_cliente = c.id_cliente
    ORDER BY v.fecha_venta DESC
    """
    cursor.execute(sql)
    ventas = cursor.fetchall()
    
    # Para cada venta, obtener sus detalles
    for venta in ventas:
        sql_detalles = "SELECT * FROM detalles_venta WHERE id_venta = %s"
        cursor.execute(sql_detalles, (venta["id_venta"],))
        venta["detalles"] = cursor.fetchall()
    
    cursor.close()
    conexion.close()
    return ventas

def ver_ventas_por_fecha(fecha_inicio: str, fecha_fin: str):
    conexion = conectar()
    if not conexion:
        return {"error": "Error de conexión a la base de datos"}
    
    cursor = conexion.cursor(dictionary=True)
    sql = """
    SELECT v.*, u.nombre as vendedor_nombre, c.nombre as cliente_nombre
    FROM ventas v
    LEFT JOIN usuarios u ON v.id_usuario = u.id_usuario
    LEFT JOIN clientes c ON v.id_cliente = c.id_cliente
    WHERE DATE(v.fecha_venta) BETWEEN %s AND %s
    ORDER BY v.fecha_venta DESC
    """
    cursor.execute(sql, (fecha_inicio, fecha_fin))
    ventas = cursor.fetchall()
    
    for venta in ventas:
        sql_detalles = "SELECT * FROM detalles_venta WHERE id_venta = %s"
        cursor.execute(sql_detalles, (venta["id_venta"],))
        venta["detalles"] = cursor.fetchall()
    
    cursor.close()
    conexion.close()
    return ventas

