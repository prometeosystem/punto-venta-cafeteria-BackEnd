from database.conexion import conectar
from schemas.venta_schema import VentaCreate
from datetime import datetime

def crear_venta(venta: VentaCreate):
    conexion = conectar()
    if not conexion:
        return {"error": "Error de conexión a la base de datos"}
    
    cursor = conexion.cursor()
    
    try:
        # Crear la venta
        sql_venta = """
        INSERT INTO ventas(id_cliente, id_usuario, total, metodo_pago, fecha_venta)
        VALUES (%s, %s, %s, %s, %s)
        """
        datos_venta = (
            venta.id_cliente, venta.id_usuario, venta.total,
            venta.metodo_pago, datetime.now()
        )
        cursor.execute(sql_venta, datos_venta)
        venta_id = cursor.lastrowid
        
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
        
        conexion.commit()
        cursor.close()
        conexion.close()
        return {"message": "Venta creada correctamente", "id_venta": venta_id}
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

