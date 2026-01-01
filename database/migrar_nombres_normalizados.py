"""
Script para migrar nombres normalizados en insumos existentes.
Ejecutar este script después de agregar el campo nombre_normalizado a la tabla insumos.
"""
import sys
import os

# Agregar el directorio raíz al path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database.conexion import conectar
from utils.normalize import normalizar_nombre

def migrar_nombres_normalizados():
    """Actualiza el campo nombre_normalizado para todos los insumos existentes"""
    conexion = conectar()
    if not conexion:
        print("Error: No se pudo conectar a la base de datos")
        return
    
    cursor = conexion.cursor(dictionary=True)
    
    try:
        # Obtener todos los insumos sin nombre_normalizado o con nombre_normalizado vacío
        sql = "SELECT id_insumo, nombre FROM insumos WHERE nombre_normalizado IS NULL OR nombre_normalizado = ''"
        cursor.execute(sql)
        insumos = cursor.fetchall()
        
        if not insumos:
            print("No hay insumos que necesiten migración.")
            return
        
        print(f"Se encontraron {len(insumos)} insumos para migrar.")
        
        # Actualizar cada insumo
        actualizados = 0
        errores = 0
        
        for insumo in insumos:
            nombre_normalizado = normalizar_nombre(insumo["nombre"])
            
            try:
                # Verificar si ya existe otro insumo con el mismo nombre normalizado
                sql_check = "SELECT id_insumo, nombre FROM insumos WHERE nombre_normalizado = %s AND id_insumo != %s"
                cursor.execute(sql_check, (nombre_normalizado, insumo["id_insumo"]))
                duplicado = cursor.fetchone()
                
                if duplicado:
                    print(f"ADVERTENCIA: El insumo '{insumo['nombre']}' (id: {insumo['id_insumo']}) tiene el mismo "
                          f"nombre normalizado que '{duplicado['nombre']}' (id: {duplicado['id_insumo']})")
                    errores += 1
                    continue
                
                # Actualizar el nombre_normalizado
                sql_update = "UPDATE insumos SET nombre_normalizado = %s WHERE id_insumo = %s"
                cursor.execute(sql_update, (nombre_normalizado, insumo["id_insumo"]))
                actualizados += 1
                print(f"✓ Actualizado: '{insumo['nombre']}' -> '{nombre_normalizado}'")
                
            except Exception as e:
                print(f"✗ Error al actualizar insumo '{insumo['nombre']}': {str(e)}")
                errores += 1
        
        conexion.commit()
        print(f"\nMigración completada:")
        print(f"  - Actualizados: {actualizados}")
        print(f"  - Errores: {errores}")
        
    except Exception as e:
        conexion.rollback()
        print(f"Error durante la migración: {str(e)}")
    finally:
        cursor.close()
        conexion.close()

if __name__ == "__main__":
    print("Iniciando migración de nombres normalizados...")
    migrar_nombres_normalizados()
    print("Migración finalizada.")


