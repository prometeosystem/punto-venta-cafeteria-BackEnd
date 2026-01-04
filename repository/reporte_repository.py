from database.conexion import conectar
from datetime import datetime, timedelta
from decimal import Decimal

def obtener_ventas_por_dia(fecha_inicio: str, fecha_fin: str):
    """Obtiene las ventas agrupadas por día"""
    conexion = conectar()
    if not conexion:
        return {"error": "Error de conexión a la base de datos"}
    
    cursor = conexion.cursor(dictionary=True)
    sql = """
    SELECT 
        DATE(fecha_venta) as fecha,
        COUNT(*) as cantidad_ventas,
        SUM(total) as total_ventas,
        AVG(total) as ticket_promedio
    FROM ventas
    WHERE DATE(fecha_venta) BETWEEN %s AND %s
    GROUP BY DATE(fecha_venta)
    ORDER BY fecha ASC
    """
    cursor.execute(sql, (fecha_inicio, fecha_fin))
    resultados = cursor.fetchall()
    
    # Convertir Decimal a float para JSON
    for resultado in resultados:
        resultado['total_ventas'] = float(resultado['total_ventas']) if resultado['total_ventas'] else 0
        resultado['ticket_promedio'] = float(resultado['ticket_promedio']) if resultado['ticket_promedio'] else 0
    
    cursor.close()
    conexion.close()
    return resultados

def obtener_productos_mas_vendidos(fecha_inicio: str, fecha_fin: str, limite: int = 10):
    """Obtiene los productos más vendidos en un período"""
    conexion = conectar()
    if not conexion:
        return {"error": "Error de conexión a la base de datos"}
    
    cursor = conexion.cursor(dictionary=True)
    sql = """
    SELECT 
        p.id_producto,
        p.nombre,
        p.categoria,
        SUM(dv.cantidad) as cantidad_vendida,
        SUM(dv.subtotal) as total_ventas,
        COUNT(DISTINCT dv.id_venta) as veces_vendido
    FROM detalles_venta dv
    JOIN productos p ON dv.id_producto = p.id_producto
    JOIN ventas v ON dv.id_venta = v.id_venta
    WHERE DATE(v.fecha_venta) BETWEEN %s AND %s
    GROUP BY p.id_producto, p.nombre, p.categoria
    ORDER BY cantidad_vendida DESC
    LIMIT %s
    """
    cursor.execute(sql, (fecha_inicio, fecha_fin, limite))
    resultados = cursor.fetchall()
    
    # Convertir Decimal a float
    for resultado in resultados:
        resultado['cantidad_vendida'] = int(resultado['cantidad_vendida']) if resultado['cantidad_vendida'] else 0
        resultado['total_ventas'] = float(resultado['total_ventas']) if resultado['total_ventas'] else 0
        resultado['veces_vendido'] = int(resultado['veces_vendido']) if resultado['veces_vendido'] else 0
    
    cursor.close()
    conexion.close()
    return resultados

def analizar_compras_recomendadas(meses_analisis: int = 3):
    """
    Analiza el consumo histórico de insumos y genera recomendaciones de compra
    para el siguiente mes basado en:
    - Consumo histórico de los últimos N meses
    - Stock actual
    - Cantidad mínima requerida
    - Proyección de consumo del siguiente mes
    """
    conexion = conectar()
    if not conexion:
        return {"error": "Error de conexión a la base de datos"}
    
    cursor = conexion.cursor(dictionary=True)
    
    # Calcular fechas
    fecha_fin = datetime.now()
    fecha_inicio = fecha_fin - timedelta(days=meses_analisis * 30)
    
    # Obtener todos los insumos activos
    cursor.execute("SELECT * FROM insumos WHERE activo = 1")
    insumos = cursor.fetchall()
    
    recomendaciones = []
    
    for insumo in insumos:
        id_insumo = insumo['id_insumo']
        nombre_insumo = insumo['nombre']
        stock_actual = float(insumo['cantidad_actual']) if insumo['cantidad_actual'] else 0
        stock_minimo = float(insumo['cantidad_minima']) if insumo['cantidad_minima'] else 0
        unidad_medida = insumo['unidad_medida']
        precio_compra = float(insumo['precio_compra']) if insumo['precio_compra'] else 0
        
        # Calcular consumo histórico (solo salidas)
        cursor.execute("""
            SELECT 
                SUM(cantidad) as consumo_total,
                COUNT(*) as movimientos
            FROM movimientos_inventario
            WHERE id_insumo = %s 
            AND tipo_movimiento = 'salida'
            AND DATE(fecha_movimiento) BETWEEN %s AND %s
        """, (id_insumo, fecha_inicio.strftime('%Y-%m-%d'), fecha_fin.strftime('%Y-%m-%d')))
        
        consumo_data = cursor.fetchone()
        consumo_total = float(consumo_data['consumo_total']) if consumo_data and consumo_data['consumo_total'] else 0
        dias_analisis = (fecha_fin - fecha_inicio).days
        dias_analisis = max(dias_analisis, 1)  # Evitar división por cero
        
        # Calcular consumo promedio diario
        consumo_promedio_diario = consumo_total / dias_analisis if dias_analisis > 0 else 0
        
        # Proyectar consumo del siguiente mes (30 días)
        consumo_proyectado_mes = consumo_promedio_diario * 30
        
        # Calcular cantidad recomendada a comprar
        # Necesitamos: consumo_proyectado + stock_minimo - stock_actual
        cantidad_recomendada = consumo_proyectado_mes + stock_minimo - stock_actual
        
        # Solo recomendar si la cantidad es positiva y significativa
        if cantidad_recomendada > 0.1:  # Mínimo 0.1 unidades
            costo_estimado = cantidad_recomendada * precio_compra if precio_compra > 0 else 0
            
            # Calcular urgencia basada en stock actual vs mínimo
            if stock_actual <= stock_minimo:
                urgencia = "alta"
            elif stock_actual <= stock_minimo * 1.5:
                urgencia = "media"
            else:
                urgencia = "baja"
            
            recomendaciones.append({
                "id_insumo": id_insumo,
                "nombre": nombre_insumo,
                "unidad_medida": unidad_medida,
                "stock_actual": round(stock_actual, 2),
                "stock_minimo": round(stock_minimo, 2),
                "consumo_promedio_diario": round(consumo_promedio_diario, 2),
                "consumo_proyectado_mes": round(consumo_proyectado_mes, 2),
                "cantidad_recomendada": round(cantidad_recomendada, 2),
                "precio_compra": round(precio_compra, 2),
                "costo_estimado": round(costo_estimado, 2),
                "urgencia": urgencia,
                "dias_restantes_estimados": round(stock_actual / consumo_promedio_diario, 1) if consumo_promedio_diario > 0 else 999
            })
    
    # Ordenar por urgencia y luego por cantidad recomendada
    orden_urgencia = {"alta": 1, "media": 2, "baja": 3}
    recomendaciones.sort(key=lambda x: (orden_urgencia[x['urgencia']], -x['cantidad_recomendada']))
    
    # Calcular totales
    total_costo_estimado = sum(r['costo_estimado'] for r in recomendaciones)
    total_insumos_urgentes = sum(1 for r in recomendaciones if r['urgencia'] == 'alta')
    
    cursor.close()
    conexion.close()
    
    return {
        "recomendaciones": recomendaciones,
        "resumen": {
            "total_insumos_recomendados": len(recomendaciones),
            "total_costo_estimado": round(total_costo_estimado, 2),
            "insumos_urgentes": total_insumos_urgentes,
            "periodo_analisis_dias": dias_analisis,
            "fecha_analisis": fecha_fin.strftime('%Y-%m-%d')
        }
    }

