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
        
        # Obtener nombre del cliente
        # Prioridad: 1) nombre_cliente del request, 2) nombre del cliente registrado
        nombre_cliente_preorden = None
        print(f"[DEBUG] Venta recibida - id_cliente: {venta.id_cliente}, nombre_cliente: {venta.nombre_cliente}")
        
        if venta.nombre_cliente and venta.nombre_cliente.strip():
            # Si se proporciona nombre_cliente directamente, usarlo
            nombre_cliente_preorden = venta.nombre_cliente.strip()
            print(f"[DEBUG] Usando nombre_cliente del request: {nombre_cliente_preorden}")
        elif venta.id_cliente:
            # Si no, buscar el nombre del cliente registrado
            cursor.execute("SELECT nombre FROM clientes WHERE id_cliente = %s", (venta.id_cliente,))
            cliente_info = cursor.fetchone()
            if cliente_info:
                nombre_cliente_preorden = cliente_info[0]  # cursor normal, acceso por índice
                print(f"[DEBUG] Usando nombre del cliente registrado: {nombre_cliente_preorden}")
            else:
                print(f"[DEBUG] Cliente ID {venta.id_cliente} no encontrado")
        else:
            print(f"[DEBUG] No se proporcionó ni nombre_cliente ni id_cliente")
        
        print(f"[DEBUG] nombre_cliente_preorden final: {nombre_cliente_preorden}")
        
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
            nombre_cliente_preorden,  # Obtener del cliente si existe
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
        
        # Crear comanda automáticamente en estado "pendiente" para que pase a barista
        # Verificar si hay productos con recetas (insumos)
        productos_con_recetas = []
        for detalle in venta.detalles:
            cursor.execute("""
                SELECT COUNT(*) as tiene_recetas 
                FROM recetas_insumos 
                WHERE id_producto = %s
            """, (detalle.id_producto,))
            resultado = cursor.fetchone()
            if resultado and resultado[0] > 0:
                productos_con_recetas.append(detalle)
        
        # Si hay productos con recetas, crear comanda en estado "pendiente"
        # Los insumos se restarán cuando la comanda se marque como "terminada"
        comanda_id = None
        if productos_con_recetas:
            # ⚠️ IMPORTANTE: Verificar si ya existe una comanda para esta venta
            # Usar cursor dictionary para acceso por nombre
            cursor_dict = conexion.cursor(dictionary=True)
            cursor_dict.execute("SELECT id_comanda FROM comandas WHERE id_venta = %s", (venta_id,))
            comanda_existente = cursor_dict.fetchone()
            cursor_dict.close()
            
            if comanda_existente:
                # Ya existe una comanda para esta venta, no crear otra
                comanda_id = comanda_existente['id_comanda']
                print(f"[DEBUG] Comanda ya existe para venta {venta_id}: ID {comanda_id}")
            else:
                # Crear la comanda en estado "pendiente"
                sql_comanda = """
                INSERT INTO comandas(id_venta, estado, fecha_creacion)
                VALUES (%s, %s, %s)
                """
                fecha_actual = datetime.now()
                cursor.execute(sql_comanda, (venta_id, 'pendiente', fecha_actual))
                comanda_id = cursor.lastrowid
                
                # Crear los detalles de la comanda
                sql_detalle_comanda = """
                INSERT INTO detalles_comanda(id_comanda, id_producto, cantidad, observaciones)
                VALUES (%s, %s, %s, %s)
                """
                for detalle in productos_con_recetas:
                    observaciones = detalle.observaciones if hasattr(detalle, 'observaciones') and detalle.observaciones else None
                    cursor.execute(sql_detalle_comanda, (
                        comanda_id, detalle.id_producto, detalle.cantidad, observaciones
                    ))
        
        conexion.commit()
        cursor.close()
        conexion.close()
        return {
            "message": "Venta creada correctamente",
            "id_venta": venta_id,
            "id_pedido": pedido_id,
            "ticket_id": ticket_id,
            "id_comanda": comanda_id,
            "comanda_creada": comanda_id is not None
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

def obtener_info_ticket_actual():
    """Obtiene información sobre el ticket actual (número secuencial del día)"""
    conexion = conectar()
    if not conexion:
        return {"error": "Error de conexión a la base de datos"}
    
    cursor = conexion.cursor(dictionary=True)
    
    try:
        # Contar tickets del día actual (incluyendo los que ya tienen ticket_id)
        fecha_hoy = datetime.now().strftime("%Y-%m-%d")
        cursor.execute("""
            SELECT COUNT(*) as total_tickets_hoy
            FROM preordenes
            WHERE DATE(fecha_creacion) = %s
        """, (fecha_hoy,))
        contador_dia = cursor.fetchone()
        
        # Obtener el último ticket_id generado
        cursor.execute("""
            SELECT ticket_id, fecha_creacion
            FROM preordenes
            WHERE ticket_id IS NOT NULL
            ORDER BY fecha_creacion DESC
            LIMIT 1
        """)
        ultimo_ticket = cursor.fetchone()
        
        # Calcular el número de ticket actual (siguiente número)
        numero_ticket_actual = (contador_dia["total_tickets_hoy"] if contador_dia else 0) + 1
        
        # Generar el siguiente ticket_id que se usaría
        siguiente_ticket_id = generar_ticket_id()
        
        cursor.close()
        conexion.close()
        
        return {
            "numero_ticket_actual": numero_ticket_actual,  # Número secuencial del día (ej: 19, 20, 21...)
            "ultimo_ticket_id": ultimo_ticket["ticket_id"] if ultimo_ticket else None,
            "fecha_ultimo_ticket": ultimo_ticket["fecha_creacion"].isoformat() if ultimo_ticket and ultimo_ticket.get("fecha_creacion") else None,
            "tickets_hoy": contador_dia["total_tickets_hoy"] if contador_dia else 0,
            "siguiente_ticket_id": siguiente_ticket_id,  # Preview del siguiente ticket_id completo
            "fecha_actual": fecha_hoy
        }
    except Exception as e:
        cursor.close()
        conexion.close()
        return {"error": f"Error al obtener información del ticket: {str(e)}"}

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

