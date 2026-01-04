#!/usr/bin/env python3
"""
Script para crear usuario administrador directamente en la base de datos.
Útil cuando el servidor no está corriendo o hay problemas con la API.
"""

import sys
import bcrypt
from database.conexion import conectar

# Credenciales del administrador
ADMIN_EMAIL = "admin@cafeteria.com"
ADMIN_PASSWORD = "admin123"
ADMIN_USER = "admin"
ADMIN_NOMBRE = "Admin"
ADMIN_APELLIDO = "Sistema"

def crear_usuario_admin():
    """Crea un usuario administrador directamente en la base de datos"""
    print("🔐 Creando usuario administrador...")
    print("")
    
    conexion = conectar()
    if not conexion:
        print("❌ Error: No se pudo conectar a la base de datos")
        print("   Verifica las credenciales en database/conexion.py")
        return False
    
    cursor = conexion.cursor(dictionary=True)
    
    # Verificar si ya existe un usuario con ese correo
    cursor.execute("SELECT id_usuario, correo FROM usuarios WHERE correo = %s", (ADMIN_EMAIL,))
    usuario_existente = cursor.fetchone()
    
    if usuario_existente:
        print(f"⚠️  Usuario administrador ya existe: {ADMIN_EMAIL}")
        print(f"   ID: {usuario_existente['id_usuario']}")
        respuesta = input("   ¿Deseas actualizar la contraseña? (s/n): ")
        if respuesta.lower() != 's':
            cursor.close()
            conexion.close()
            return True
        
        # Actualizar contraseña
        contrasena_hash = bcrypt.hashpw(ADMIN_PASSWORD.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        cursor.execute("""
            UPDATE usuarios 
            SET contrasena = %s, user = %s, activo = TRUE
            WHERE correo = %s
        """, (contrasena_hash, ADMIN_USER, ADMIN_EMAIL))
        conexion.commit()
        print(f"✅ Contraseña actualizada para: {ADMIN_EMAIL}")
        cursor.close()
        conexion.close()
        return True
    
    # Crear usuario administrador
    contrasena_hash = bcrypt.hashpw(ADMIN_PASSWORD.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
    
    try:
        cursor.execute("""
            INSERT INTO usuarios (nombre, apellido_paterno, correo, user, contrasena, rol, activo)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """, (ADMIN_NOMBRE, ADMIN_APELLIDO, ADMIN_EMAIL, ADMIN_USER, contrasena_hash, "superadministrador", True))
        conexion.commit()
        print(f"✅ Usuario administrador creado exitosamente")
        print("")
        print("📋 Credenciales:")
        print(f"   Email: {ADMIN_EMAIL}")
        print(f"   Usuario: {ADMIN_USER}")
        print(f"   Contraseña: {ADMIN_PASSWORD}")
        print(f"   Rol: superadministrador")
        print("")
        print("⚠️  IMPORTANTE: Cambia estas credenciales en producción")
        cursor.close()
        conexion.close()
        return True
    except Exception as e:
        print(f"❌ Error al crear usuario: {e}")
        conexion.rollback()
        cursor.close()
        conexion.close()
        return False

if __name__ == "__main__":
    print("=" * 50)
    print("🚀 Crear Usuario Administrador - Modo Directo")
    print("=" * 50)
    print("")
    
    if crear_usuario_admin():
        print("=" * 50)
        print("✅ Proceso completado")
        print("=" * 50)
        sys.exit(0)
    else:
        print("=" * 50)
        print("❌ Error en el proceso")
        print("=" * 50)
        sys.exit(1)

