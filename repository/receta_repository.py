from database.conexion import conectar
from schemas.comanda_schema import RecetaInsumoCreate

def crear_receta(receta: RecetaInsumoCreate):
    conexion = conectar()
    if not conexion:
        return {"error": "Error de conexión a la base de datos"}
    
    cursor = conexion.cursor()
    
    # Verificar si existe la columna unidad_medida
    try:
        cursor.execute("""
            SELECT COUNT(*) as existe 
            FROM INFORMATION_SCHEMA.COLUMNS 
            WHERE TABLE_SCHEMA = DATABASE() 
            AND TABLE_NAME = 'recetas_insumos' 
            AND COLUMN_NAME = 'unidad_medida'
        """)
        tiene_unidad_medida = cursor.fetchone()[0] > 0
    except:
        tiene_unidad_medida = False
    
    if tiene_unidad_medida:
        sql = """
        INSERT INTO recetas_insumos(id_producto, id_insumo, cantidad_necesaria, unidad_medida)
        VALUES (%s, %s, %s, %s)
        """
        datos = (receta.id_producto, receta.id_insumo, receta.cantidad_necesaria, receta.unidad_medida)
    else:
        sql = """
        INSERT INTO recetas_insumos(id_producto, id_insumo, cantidad_necesaria)
        VALUES (%s, %s, %s)
        """
        datos = (receta.id_producto, receta.id_insumo, receta.cantidad_necesaria)
    
    try:
        cursor.execute(sql, datos)
        conexion.commit()
        receta_id = cursor.lastrowid
        cursor.close()
        conexion.close()
        return {"message": "Receta creada correctamente", "id_receta": receta_id}
    except Exception as e:
        conexion.rollback()
        cursor.close()
        conexion.close()
        return {"error": f"Error al crear receta: {str(e)}"}

def ver_recetas_por_producto(id_producto: int):
    conexion = conectar()
    if not conexion:
        return {"error": "Error de conexión a la base de datos"}
    
    cursor = conexion.cursor(dictionary=True)
    
    # Verificar si existe la columna unidad_medida en recetas
    try:
        cursor.execute("""
            SELECT COUNT(*) as existe 
            FROM INFORMATION_SCHEMA.COLUMNS 
            WHERE TABLE_SCHEMA = DATABASE() 
            AND TABLE_NAME = 'recetas_insumos' 
            AND COLUMN_NAME = 'unidad_medida'
        """)
        tiene_unidad_medida = cursor.fetchone()[0] > 0
    except:
        tiene_unidad_medida = False
    
    if tiene_unidad_medida:
        # ⚠️ IMPORTANTE: Usar alias para unidad_medida de receta para evitar conflicto con insumo
        # La unidad_medida de la receta debe tener prioridad sobre la del insumo
        sql = """
        SELECT r.id_receta, r.id_producto, r.id_insumo, r.cantidad_necesaria, 
               r.unidad_medida,
               i.nombre as insumo_nombre, 
               i.unidad_medida as unidad_medida_insumo,
               p.nombre as producto_nombre
        FROM recetas_insumos r
        JOIN insumos i ON r.id_insumo = i.id_insumo
        JOIN productos p ON r.id_producto = p.id_producto
        WHERE r.id_producto = %s
        """
    else:
        sql = """
        SELECT r.*, i.nombre as insumo_nombre, i.unidad_medida as unidad_medida_insumo, p.nombre as producto_nombre
        FROM recetas_insumos r
        JOIN insumos i ON r.id_insumo = i.id_insumo
        JOIN productos p ON r.id_producto = p.id_producto
        WHERE r.id_producto = %s
        """
    
    cursor.execute(sql, (id_producto,))
    recetas = cursor.fetchall()
    cursor.close()
    conexion.close()
    return recetas

def eliminar_receta(id_receta: int):
    conexion = conectar()
    if not conexion:
        return {"error": "Error de conexión a la base de datos"}
    
    cursor = conexion.cursor()
    sql = "DELETE FROM recetas_insumos WHERE id_receta = %s"
    
    try:
        cursor.execute(sql, (id_receta,))
        conexion.commit()
        if cursor.rowcount == 0:
            cursor.close()
            conexion.close()
            return {"error": "Receta no encontrada"}
        cursor.close()
        conexion.close()
        return {"message": "Receta eliminada correctamente"}
    except Exception as e:
        conexion.rollback()
        cursor.close()
        conexion.close()
        return {"error": f"Error al eliminar receta: {str(e)}"}

def eliminar_todas_recetas_producto(id_producto: int):
    """Elimina todas las recetas de un producto"""
    conexion = conectar()
    if not conexion:
        return {"error": "Error de conexión a la base de datos"}
    
    cursor = conexion.cursor()
    sql = "DELETE FROM recetas_insumos WHERE id_producto = %s"
    
    try:
        cursor.execute(sql, (id_producto,))
        conexion.commit()
        recetas_eliminadas = cursor.rowcount
        cursor.close()
        conexion.close()
        return {"message": f"Recetas eliminadas correctamente", "recetas_eliminadas": recetas_eliminadas}
    except Exception as e:
        conexion.rollback()
        cursor.close()
        conexion.close()
        return {"error": f"Error al eliminar recetas: {str(e)}"}

