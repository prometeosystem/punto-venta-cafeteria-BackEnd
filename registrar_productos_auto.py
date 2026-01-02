#!/usr/bin/env python3
"""
Script para registrar automáticamente todos los productos en la base de datos.
Primero verifica si hay un usuario administrador, si no, crea uno.
Luego hace login y registra todos los productos.
"""

import requests
import json
import time
import sys
from database.conexion import conectar

BASE_URL = "http://localhost:8000"

# Credenciales del administrador por defecto
ADMIN_EMAIL = "admin@cafeteria.com"
ADMIN_PASSWORD = "admin123"

def verificar_servidor():
    """Verifica si el servidor está corriendo"""
    try:
        response = requests.get(f"{BASE_URL}/health", timeout=2)
        return response.status_code == 200
    except:
        return False

def verificar_usuario_admin():
    """Verifica si el usuario administrador existe"""
    conexion = conectar()
    if not conexion:
        print("❌ Error: No se pudo conectar a la base de datos")
        return False
    
    cursor = conexion.cursor(dictionary=True)
    
    # Verificar si ya existe un usuario con ese correo
    cursor.execute("SELECT id_usuario FROM usuarios WHERE correo = %s", (ADMIN_EMAIL,))
    usuario = cursor.fetchone()
    cursor.close()
    conexion.close()
    
    if usuario:
        print(f"✅ Usuario administrador encontrado: {ADMIN_EMAIL}")
        return True
    else:
        print(f"⚠️  Usuario administrador no encontrado: {ADMIN_EMAIL}")
        print("   Por favor, crea el usuario manualmente o verifica las credenciales")
        return False

def hacer_login():
    """Hace login y retorna el token"""
    try:
        response = requests.post(
            f"{BASE_URL}/api/login",
            json={"correo": ADMIN_EMAIL, "contrasena": ADMIN_PASSWORD},
            timeout=5
        )
        if response.status_code == 200:
            data = response.json()
            return data.get("access_token")
        else:
            print(f"❌ Error en login: {response.status_code} - {response.text}")
            return None
    except Exception as e:
        print(f"❌ Error al hacer login: {e}")
        return None

def crear_producto(token, nombre, descripcion, precio, categoria):
    """Crea un producto usando la API"""
    try:
        response = requests.post(
            f"{BASE_URL}/api/productos/crear_producto",
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {token}"
            },
            json={
                "nombre": nombre,
                "descripcion": descripcion,
                "precio": float(precio),
                "categoria": categoria,
                "activo": True
            },
            timeout=5
        )
        if response.status_code == 200:
            return True, response.json()
        else:
            return False, response.text
    except Exception as e:
        return False, str(e)

def main():
    print("🚀 Iniciando registro automático de productos...")
    print("")
    
    # Verificar servidor
    print("1️⃣ Verificando servidor...")
    if not verificar_servidor():
        print("❌ El servidor no está corriendo en http://localhost:8000")
        print("   Por favor, inicia el servidor con: uvicorn main:app --reload")
        sys.exit(1)
    print("✅ Servidor está corriendo")
    print("")
    
    # Verificar usuario admin
    print("2️⃣ Verificando usuario administrador...")
    verificar_usuario_admin()  # Solo verifica, no crea
    print("")
    
    # Hacer login
    print("3️⃣ Haciendo login...")
    token = hacer_login()
    if not token:
        print("❌ No se pudo obtener el token de autenticación")
        sys.exit(1)
    print("✅ Login exitoso")
    print("")
    
    # Lista de productos a registrar
    productos = [
        # BEBIDAS CALIENTES
        ("Americano M", "Pa' empezar el día.", 40.00, "Bebidas Calientes"),
        ("Americano G", "Pa' empezar el día.", 45.00, "Bebidas Calientes"),
        ("Capuchino M", "Expresso sencillo con leche espumada.", 55.00, "Bebidas Calientes"),
        ("Capuchino G", "Expresso sencillo con leche espumada.", 60.00, "Bebidas Calientes"),
        ("Energy Latte M", "Expresso doble con leche cremosa.", 60.00, "Bebidas Calientes"),
        ("Energy Latte G", "Expresso doble con leche cremosa.", 65.00, "Bebidas Calientes"),
        ("Coco Yuki Latte M", "Expresso doble con toque sabor coco y leche cremosa.", 65.00, "Bebidas Calientes"),
        ("Coco Yuki Latte G", "Expresso doble con toque sabor coco y leche cremosa.", 69.00, "Bebidas Calientes"),
        ("Chai ó Matcha M", "Tés con leche cremosa.", 60.00, "Bebidas Calientes"),
        ("Chai ó Matcha G", "Tés con leche cremosa.", 65.00, "Bebidas Calientes"),
        ("Chai Sucio M", "Té especiado con expresso café y leche cremosa.", 65.00, "Bebidas Calientes"),
        ("Chai Sucio G", "Té especiado con expresso café y leche cremosa.", 70.00, "Bebidas Calientes"),
        ("Muka Rush M", "Expresso con chocolate y leche cremosa.", 65.00, "Bebidas Calientes"),
        ("Muka Rush G", "Expresso con chocolate y leche cremosa.", 70.00, "Bebidas Calientes"),
        ("Chocolate Dark Finish M", "Chocolate de tu elección con leche cremosa.", 65.00, "Bebidas Calientes"),
        ("Chocolate Dark Finish G", "Chocolate de tu elección con leche cremosa.", 70.00, "Bebidas Calientes"),
        ("Caramel | Irlandés M", "Expresso acompañado del sabor a elección y leche cremosa.", 65.00, "Bebidas Calientes"),
        ("Caramel | Irlandés G", "Expresso acompañado del sabor a elección y leche cremosa.", 70.00, "Bebidas Calientes"),
        
        # BEBIDAS FRÍAS
        ("Affogato", "Bola de helado acompañada de expresso doble.", 65.00, "Bebidas Frías"),
        ("Iced Americano M", "Elige tu americano helado o frapeado.", 50.00, "Bebidas Frías"),
        ("Iced Americano G", "Elige tu americano helado o frapeado.", 55.00, "Bebidas Frías"),
        ("Iced Latte M", "Elige tu latte helado o frapeado.", 55.00, "Bebidas Frías"),
        ("Iced Latte G", "Elige tu latte helado o frapeado.", 60.00, "Bebidas Frías"),
        ("Expresso Honey M", "Expresso doble + miel + agua tónica", 55.00, "Bebidas Frías"),
        ("Expresso Honey G", "Expresso doble + miel + agua tónica", 60.00, "Bebidas Frías"),
        ("Expresso Tonic M", "Expresso doble + agua tónica", 50.00, "Bebidas Frías"),
        ("Expresso Tonic G", "Expresso doble + agua tónica", 55.00, "Bebidas Frías"),
        ("Orange Coffee M", "Expresso doble + jugo de naranja + agua tónica", 65.00, "Bebidas Frías"),
        ("Orange Coffee G", "Expresso doble + jugo de naranja + agua tónica", 70.00, "Bebidas Frías"),
        ("Coco Yuki Latte Frío M", "Elígelo helado o frapeado", 70.00, "Bebidas Frías"),
        ("Coco Yuki Latte Frío G", "Elígelo helado o frapeado", 75.00, "Bebidas Frías"),
        ("Chai ó Matcha Frío M", "Elígelo helado o frapeado", 70.00, "Bebidas Frías"),
        ("Chai ó Matcha Frío G", "Elígelo helado o frapeado", 75.00, "Bebidas Frías"),
        ("Moka Rush Frío M", "Expresso con chocolate helado o frapeado", 65.00, "Bebidas Frías"),
        ("Moka Rush Frío G", "Expresso con chocolate helado o frapeado", 70.00, "Bebidas Frías"),
        ("Chocolate Dark Finish Frío M", "Chocolate de tu gusto helado o frapeado", 60.00, "Bebidas Frías"),
        ("Chocolate Dark Finish Frío G", "Chocolate de tu gusto helado o frapeado", 65.00, "Bebidas Frías"),
        ("Caramel | Irlandés | Pistache | Taro M", "Elígelo helado o frapeado", 70.00, "Bebidas Frías"),
        ("Caramel | Irlandés | Pistache | Taro G", "Elígelo helado o frapeado", 75.00, "Bebidas Frías"),
        ("Smoothie de Mango ó Fresa M", "Frappé base agua ó leche de tu fruta favorita", 70.00, "Bebidas Frías"),
        ("Smoothie de Mango ó Fresa G", "Frappé base agua ó leche de tu fruta favorita", 75.00, "Bebidas Frías"),
        
        # BEBIDAS FITNESS - ENTRENAMIENTO
        ("Sprint shot", "Un expresso doble de energía para activar tu entrenamiento.", 40.00, "Bebidas Fitness"),
        ("Peak point macchiato", "Expresso doble con un toque de espuma de leche, un boost suave pero decidido.", 45.00, "Bebidas Fitness"),
        ("Flat White Run", "Expresso doble con leche cremosa, ideal para enfoque sostenido.", 55.00, "Bebidas Fitness"),
        ("Long Run Americano", "Ligero y limpio para resistencia prolongada.", 50.00, "Bebidas Fitness"),
        ("Energy Latte Fitness", "Clásico expresso doble con leche para recuperar energía.", 65.00, "Bebidas Fitness"),
        
        # BEBIDAS FITNESS - CON PROTEÍNA/CREATINA
        ("Recovery Dúo Fruit", "Bebida base leche + plátano + fresas + scoop", 65.00, "Bebidas Fitness"),
        ("Power Boost Latte", "Bebida base leche + café + scoop", 65.00, "Bebidas Fitness"),
        ("Muscle Peanut", "Bebida base leche + crema de cacahuate + plátano + scoop", 70.00, "Bebidas Fitness"),
        ("Mango Marathon", "Bebida base leche + mango + miel + yogurt griego + scoop", 75.00, "Bebidas Fitness"),
        ("Speed Up Red", "Bebida base yogurt griego + frutos rojos + avena + scoop", 78.00, "Bebidas Fitness"),
        ("Zona Pro Matcha", "Bebida base leche + matcha + miel + fresas + scoop", 80.00, "Bebidas Fitness"),
        ("Core Blue", "Bebida base leche + moras + plátano + espirulina azul + scoop", 80.00, "Bebidas Fitness"),
        ("Antioxidant Fruit", "Agua de coco + espirulina azul + fresas + avena + scoop", 85.00, "Bebidas Fitness"),
        ("Runner Brew", "Bebida base yogurt griego + mango + miel + matcha + scoop", 88.00, "Bebidas Fitness"),
        
        # MENÚ DULCE
        ("Yogur Bloom", "Yogurt griego + granola + miel + fruta de temporada", 98.00, "Menú Dulce"),
        ("Pan de temporada", "Pregunta por disponibilidad del pan recién horneado", 75.00, "Menú Dulce"),
        ("Chocobanana Sando", "Chocolate y plátano", 67.00, "Menú Dulce"),
        ("Fruit Sando", "Fresas, durazno y kiwi", 89.00, "Menú Dulce"),
        ("Ichigo Sando", "Fresas frescas", 92.00, "Menú Dulce"),
        
        # MENÚ SALADO
        ("Classic Sando", "Jamón, queso y tocino dulce crujiente", 89.00, "Menú Salado"),
        ("Tamago Sando", "Ensalada de huevo", 60.00, "Menú Salado"),
        ("Mila Sando", "Milanesa de res", 145.00, "Menú Salado"),
        
        # ENSALADAS
        ("Huevito Bowl", "Bowl a base de lechuga italiana, espinaca, zanahoria, betabel. Cherry, huevo duro y aderezo a elección", 125.00, "Ensaladas"),
        ("Tuna fit", "Bowl a base de lechuga italiana, espinaca, zanahoria, betabel. Cherry, atún y aderezo a elección", 135.00, "Ensaladas"),
        ("Mlla Green", "Bowl a base de lechuga italiana, espinaca, zanahoria, betabel. Cherry, milanesa de res, empanizado de la casa", 145.00, "Ensaladas"),
        
        # OTROS
        ("Molletes", "Pan de la casa, frijoles, queso manchego, pico de gallo, chorizo o huevo", 0.00, "Otros"),
        ("Chilaquiles", "Totopos, crema, queso, salsa de la casa, huevo ó pollo, acompañados de frijoles refritos", 0.00, "Otros"),
    ]
    
    # Registrar productos
    print("4️⃣ Registrando productos...")
    print("")
    exitosos = 0
    errores = 0
    
    for i, (nombre, descripcion, precio, categoria) in enumerate(productos, 1):
        success, result = crear_producto(token, nombre, descripcion, precio, categoria)
        if success:
            exitosos += 1
            print(f"✅ [{i}/{len(productos)}] {nombre}")
        else:
            errores += 1
            print(f"❌ [{i}/{len(productos)}] {nombre} - Error: {result}")
        time.sleep(0.1)  # Pequeña pausa para no sobrecargar el servidor
    
    print("")
    print("=" * 50)
    print(f"✅ Productos registrados exitosamente: {exitosos}")
    if errores > 0:
        print(f"❌ Productos con error: {errores}")
    print("=" * 50)

if __name__ == "__main__":
    main()

