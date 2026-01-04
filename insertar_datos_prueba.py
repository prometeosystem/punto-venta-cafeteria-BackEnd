#!/usr/bin/env python3
"""
Script para insertar datos de prueba en la base de datos
para poder visualizar reportes en el frontend
"""

import sys
from datetime import datetime, timedelta
from database.conexion import conectar
import random

def insertar_datos_prueba():
    """Inserta ventas de prueba con diferentes fechas"""
    print("🔄 Insertando datos de prueba...")
    print("")
    
    conexion = conectar()
    if not conexion:
        print("❌ Error: No se pudo conectar a la base de datos")
        return False
    
    cursor = conexion.cursor(dictionary=True)
    
    try:
        # Verificar si hay productos, si no, crear algunos de prueba
        cursor.execute("SELECT id_producto, nombre, precio FROM productos WHERE activo = 1 LIMIT 20")
        productos = cursor.fetchall()
        
        if not productos:
            print("⚠️  No hay productos. Creando productos de prueba...")
            
            productos_prueba = [
                ("Americano M", "Café americano mediano", 40.00, "Bebidas Calientes"),
                ("Capuchino M", "Capuchino mediano", 55.00, "Bebidas Calientes"),
                ("Latte M", "Latte mediano", 60.00, "Bebidas Calientes"),
                ("Iced Americano M", "Americano helado mediano", 50.00, "Bebidas Frías"),
                ("Iced Latte M", "Latte helado mediano", 55.00, "Bebidas Frías"),
                ("Moka Rush M", "Moka rush mediano", 65.00, "Bebidas Calientes"),
                ("Chai Latte M", "Chai latte mediano", 60.00, "Bebidas Calientes"),
                ("Smoothie Mango M", "Smoothie de mango mediano", 70.00, "Bebidas Frías"),
                ("Classic Sando", "Sándwich clásico", 89.00, "Menú Salado"),
                ("Yogur Bloom", "Yogurt con granola y fruta", 98.00, "Menú Dulce"),
            ]
            
            for nombre, descripcion, precio, categoria in productos_prueba:
                sql_producto = """
                INSERT INTO productos(nombre, descripcion, precio, categoria, activo)
                VALUES (%s, %s, %s, %s, 1)
                """
                cursor.execute(sql_producto, (nombre, descripcion, precio, categoria))
            
            conexion.commit()
            print(f"✅ Creados {len(productos_prueba)} productos de prueba")
            
            # Obtener los productos recién creados
            cursor.execute("SELECT id_producto, nombre, precio FROM productos WHERE activo = 1")
            productos = cursor.fetchall()
        
        print(f"✅ Encontrados {len(productos)} productos")
        
        # Obtener usuario admin
        cursor.execute("SELECT id_usuario FROM usuarios WHERE rol = 'superadministrador' LIMIT 1")
        usuario = cursor.fetchone()
        if not usuario:
            print("❌ No se encontró usuario administrador")
            cursor.close()
            conexion.close()
            return False
        
        id_usuario = usuario['id_usuario']
        print(f"✅ Usuario ID: {id_usuario}")
        
        # Métodos de pago
        metodos_pago = ['efectivo', 'tarjeta', 'transferencia']
        
        # Crear ventas para los últimos 30 días
        ventas_creadas = 0
        fecha_actual = datetime.now()
        
        print("")
        print("📊 Creando ventas de prueba...")
        
        for dia in range(30, 0, -1):  # Últimos 30 días
            fecha_venta = fecha_actual - timedelta(days=dia)
            
            # Crear entre 2 y 8 ventas por día
            num_ventas_dia = random.randint(2, 8)
            
            for venta_num in range(num_ventas_dia):
                # Seleccionar productos aleatorios (1 a 4 productos por venta)
                num_productos = random.randint(1, 4)
                productos_venta = random.sample(productos, min(num_productos, len(productos)))
                
                # Calcular total
                total = 0
                detalles = []
                
                for producto in productos_venta:
                    cantidad = random.randint(1, 3)
                    precio_unitario = float(producto['precio'])
                    subtotal = precio_unitario * cantidad
                    total += subtotal
                    
                    detalles.append({
                        'id_producto': producto['id_producto'],
                        'cantidad': cantidad,
                        'precio_unitario': precio_unitario,
                        'subtotal': subtotal
                    })
                
                # Crear venta
                metodo_pago = random.choice(metodos_pago)
                
                # Ajustar hora de la venta (distribuir durante el día)
                hora_venta = random.randint(8, 20)  # Entre 8 AM y 8 PM
                minuto_venta = random.randint(0, 59)
                fecha_venta_completa = fecha_venta.replace(hour=hora_venta, minute=minuto_venta, second=0, microsecond=0)
                
                sql_venta = """
                INSERT INTO ventas(id_cliente, id_usuario, total, metodo_pago, fecha_venta)
                VALUES (%s, %s, %s, %s, %s)
                """
                cursor.execute(sql_venta, (
                    None,  # Sin cliente
                    id_usuario,
                    total,
                    metodo_pago,
                    fecha_venta_completa
                ))
                
                id_venta = cursor.lastrowid
                
                # Crear detalles de venta
                sql_detalle = """
                INSERT INTO detalles_venta(id_venta, id_producto, cantidad, precio_unitario, subtotal)
                VALUES (%s, %s, %s, %s, %s)
                """
                
                for detalle in detalles:
                    cursor.execute(sql_detalle, (
                        id_venta,
                        detalle['id_producto'],
                        detalle['cantidad'],
                        detalle['precio_unitario'],
                        detalle['subtotal']
                    ))
                
                ventas_creadas += 1
        
        # Crear insumos si no existen
        print("")
        print("📦 Verificando insumos...")
        
        cursor.execute("SELECT id_insumo, nombre FROM insumos WHERE activo = 1 LIMIT 10")
        insumos = cursor.fetchall()
        
        if not insumos:
            print("⚠️  No hay insumos. Creando insumos de prueba...")
            
            insumos_prueba = [
                ("Café en grano", "Café arábica premium", "kg", 10.0, 2.0, 150.00),
                ("Leche entera", "Leche fresca", "litros", 20.0, 5.0, 25.00),
                ("Azúcar", "Azúcar blanca", "kg", 5.0, 1.0, 30.00),
                ("Chocolate", "Chocolate para bebidas", "kg", 3.0, 0.5, 80.00),
                ("Canela", "Canela en polvo", "kg", 1.0, 0.2, 120.00),
                ("Vainilla", "Extracto de vainilla", "litros", 2.0, 0.5, 150.00),
                ("Hielo", "Cubos de hielo", "kg", 50.0, 10.0, 5.00),
                ("Pan", "Pan para sándwiches", "unidades", 30.0, 10.0, 2.50),
                ("Queso", "Queso manchego", "kg", 5.0, 1.0, 120.00),
                ("Jamón", "Jamón de pavo", "kg", 3.0, 0.5, 180.00),
            ]
            
            for nombre, descripcion, unidad, cantidad_actual, cantidad_minima, precio_compra in insumos_prueba:
                sql_insumo = """
                INSERT INTO insumos(nombre, descripcion, unidad_medida, cantidad_actual, cantidad_minima, precio_compra, activo)
                VALUES (%s, %s, %s, %s, %s, %s, 1)
                """
                cursor.execute(sql_insumo, (nombre, descripcion, unidad, cantidad_actual, cantidad_minima, precio_compra))
            
            conexion.commit()
            print(f"✅ Creados {len(insumos_prueba)} insumos de prueba")
            
            # Obtener los insumos recién creados
            cursor.execute("SELECT id_insumo, nombre FROM insumos WHERE activo = 1")
            insumos = cursor.fetchall()
        
        # Crear algunos movimientos de inventario para el análisis de compras
        print("")
        print("📦 Creando movimientos de inventario...")
        
        if insumos:
            movimientos_creados = 0
            # Crear movimientos de salida (consumo) para los últimos 90 días
            for dia in range(90, 0, -1):
                fecha_movimiento = fecha_actual - timedelta(days=dia)
                
                # Crear algunos movimientos aleatorios
                if random.random() < 0.3:  # 30% de probabilidad de movimiento por día
                    insumo = random.choice(insumos)
                    cantidad = round(random.uniform(0.1, 5.0), 2)
                    
                    sql_movimiento = """
                    INSERT INTO movimientos_inventario(
                        id_insumo, tipo_movimiento, cantidad, motivo, fecha_movimiento
                    )
                    VALUES (%s, 'salida', %s, 'Consumo por ventas', %s)
                    """
                    cursor.execute(sql_movimiento, (
                        insumo['id_insumo'],
                        cantidad,
                        fecha_movimiento
                    ))
                    movimientos_creados += 1
            
            print(f"✅ Creados {movimientos_creados} movimientos de inventario")
        
        conexion.commit()
        cursor.close()
        conexion.close()
        
        print("")
        print("=" * 50)
        print(f"✅ Datos de prueba insertados exitosamente")
        print(f"   - Ventas creadas: {ventas_creadas}")
        print(f"   - Período: últimos 30 días")
        print("=" * 50)
        print("")
        print("💡 Ahora puedes ver los reportes en el frontend")
        
        return True
        
    except Exception as e:
        conexion.rollback()
        cursor.close()
        conexion.close()
        print(f"❌ Error al insertar datos: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("=" * 50)
    print("🚀 Insertar Datos de Prueba - Reportes")
    print("=" * 50)
    print("")
    
    if insertar_datos_prueba():
        print("=" * 50)
        print("✅ Proceso completado")
        print("=" * 50)
        sys.exit(0)
    else:
        print("=" * 50)
        print("❌ Error en el proceso")
        print("=" * 50)
        sys.exit(1)

