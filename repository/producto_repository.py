from database.conexion import conectar
from schemas.producto_schema import ProductoCreate, ProductoUpdate

def crear_producto(producto: ProductoCreate, imagen_bytes: bytes = None, tipo_imagen: str = None):
    conexion = conectar()
    if not conexion:
        return {"error": "Error de conexión a la base de datos"}
    
    cursor = conexion.cursor()
    
    # Verificar si existe la columna imagen
    try:
        cursor.execute("""
            SELECT COUNT(*) as existe 
            FROM INFORMATION_SCHEMA.COLUMNS 
            WHERE TABLE_SCHEMA = DATABASE() 
            AND TABLE_NAME = 'productos' 
            AND COLUMN_NAME = 'imagen'
        """)
        tiene_imagen_col = cursor.fetchone()[0] > 0
    except:
        tiene_imagen_col = False
    
    if imagen_bytes and tiene_imagen_col:
        sql = """
        INSERT INTO productos(nombre, descripcion, precio, categoria, imagen, tipo_imagen, activo)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
        """
        datos = (
            producto.nombre, producto.descripcion, producto.precio,
            producto.categoria, imagen_bytes, tipo_imagen, producto.activo
        )
    else:
        sql = """
        INSERT INTO productos(nombre, descripcion, precio, categoria, activo)
        VALUES (%s, %s, %s, %s, %s)
        """
        datos = (
            producto.nombre, producto.descripcion, producto.precio,
            producto.categoria, producto.activo
        )
    
    try:
        cursor.execute(sql, datos)
        conexion.commit()
        producto_id = cursor.lastrowid
        cursor.close()
        conexion.close()
        return {"message": "Producto creado correctamente", "id_producto": producto_id}
    except Exception as e:
        conexion.rollback()
        cursor.close()
        conexion.close()
        return {"error": f"Error al crear producto: {str(e)}"}

def ver_todos_productos():
    conexion = conectar()
    if not conexion:
        return {"error": "Error de conexión a la base de datos"}
    
    cursor = conexion.cursor(dictionary=True)
    # Verificar si existe la columna tipo_imagen
    try:
        cursor.execute("""
            SELECT COUNT(*) as existe 
            FROM INFORMATION_SCHEMA.COLUMNS 
            WHERE TABLE_SCHEMA = DATABASE() 
            AND TABLE_NAME = 'productos' 
            AND COLUMN_NAME = 'tipo_imagen'
        """)
        tiene_imagen = cursor.fetchone()['existe'] > 0
        
        if tiene_imagen:
            sql = """
            SELECT id_producto, nombre, descripcion, precio, categoria, 
                   tipo_imagen, activo, fecha_creacion, fecha_actualizacion
            FROM productos WHERE activo = 1
            """
        else:
            sql = """
            SELECT id_producto, nombre, descripcion, precio, categoria, 
                   activo, fecha_creacion, fecha_actualizacion
            FROM productos WHERE activo = 1
            """
    except:
        # Si hay error, usar query sin tipo_imagen
        sql = """
        SELECT id_producto, nombre, descripcion, precio, categoria, 
               activo, fecha_creacion, fecha_actualizacion
        FROM productos WHERE activo = 1
        """
    
    cursor.execute(sql)
    filas = cursor.fetchall()
    cursor.close()
    conexion.close()
    return filas

def ver_producto_by_id(id_producto: int):
    conexion = conectar()
    if not conexion:
        return {"error": "Error de conexión a la base de datos"}
    
    cursor = conexion.cursor(dictionary=True)
    # Verificar si existe la columna tipo_imagen
    try:
        cursor.execute("""
            SELECT COUNT(*) as existe 
            FROM INFORMATION_SCHEMA.COLUMNS 
            WHERE TABLE_SCHEMA = DATABASE() 
            AND TABLE_NAME = 'productos' 
            AND COLUMN_NAME = 'tipo_imagen'
        """)
        tiene_imagen = cursor.fetchone()['existe'] > 0
        
        if tiene_imagen:
            sql = """
            SELECT id_producto, nombre, descripcion, precio, categoria, 
                   tipo_imagen, activo, fecha_creacion, fecha_actualizacion
            FROM productos WHERE id_producto = %s
            """
        else:
            sql = """
            SELECT id_producto, nombre, descripcion, precio, categoria, 
                   activo, fecha_creacion, fecha_actualizacion
            FROM productos WHERE id_producto = %s
            """
    except:
        # Si hay error, usar query sin tipo_imagen
        sql = """
        SELECT id_producto, nombre, descripcion, precio, categoria, 
               activo, fecha_creacion, fecha_actualizacion
        FROM productos WHERE id_producto = %s
        """
    
    cursor.execute(sql, (id_producto,))
    producto = cursor.fetchone()
    cursor.close()
    conexion.close()
    
    if not producto:
        return {"error": "Producto no encontrado"}
    return producto

def obtener_imagen_producto(id_producto: int):
    """Obtiene la imagen de un producto desde la base de datos"""
    conexion = conectar()
    if not conexion:
        return {"error": "Error de conexión a la base de datos"}
    
    cursor = conexion.cursor()
    
    # Verificar si existe la columna imagen
    try:
        cursor.execute("""
            SELECT COUNT(*) as existe 
            FROM INFORMATION_SCHEMA.COLUMNS 
            WHERE TABLE_SCHEMA = DATABASE() 
            AND TABLE_NAME = 'productos' 
            AND COLUMN_NAME = 'imagen'
        """)
        tiene_imagen_col = cursor.fetchone()[0] > 0
    except:
        tiene_imagen_col = False
    
    if not tiene_imagen_col:
        cursor.close()
        conexion.close()
        return {"error": "La funcionalidad de imágenes no está disponible. Ejecute la migración."}
    
    sql = "SELECT imagen, tipo_imagen FROM productos WHERE id_producto = %s"
    cursor.execute(sql, (id_producto,))
    resultado = cursor.fetchone()
    cursor.close()
    conexion.close()
    
    if not resultado or not resultado[0]:
        return {"error": "Imagen no encontrada"}
    
    return {
        "imagen": resultado[0],
        "tipo_imagen": resultado[1]
    }

def editar_producto(id_producto: int, producto: ProductoUpdate, imagen_bytes: bytes = None, tipo_imagen: str = None, eliminar_imagen: bool = False):
    conexion = conectar()
    if not conexion:
        return {"error": "Error de conexión a la base de datos"}
    
    cursor = conexion.cursor()
    
    # Verificar si existe la columna imagen
    try:
        cursor.execute("""
            SELECT COUNT(*) as existe 
            FROM INFORMATION_SCHEMA.COLUMNS 
            WHERE TABLE_SCHEMA = DATABASE() 
            AND TABLE_NAME = 'productos' 
            AND COLUMN_NAME = 'imagen'
        """)
        tiene_imagen_col = cursor.fetchone()[0] > 0
    except:
        tiene_imagen_col = False
    
    campos = []
    valores = []
    
    if producto.nombre is not None:
        campos.append("nombre = %s")
        valores.append(producto.nombre)
    if producto.descripcion is not None:
        campos.append("descripcion = %s")
        valores.append(producto.descripcion)
    if producto.precio is not None:
        campos.append("precio = %s")
        valores.append(producto.precio)
    if producto.categoria is not None:
        campos.append("categoria = %s")
        valores.append(producto.categoria)
    if producto.activo is not None:
        campos.append("activo = %s")
        valores.append(producto.activo)
    
    # Manejar imagen solo si la columna existe
    if tiene_imagen_col:
        if eliminar_imagen:
            campos.append("imagen = NULL")
            campos.append("tipo_imagen = NULL")
        elif imagen_bytes and tipo_imagen:
            campos.append("imagen = %s")
            campos.append("tipo_imagen = %s")
            valores.append(imagen_bytes)
            valores.append(tipo_imagen)
    
    if not campos:
        cursor.close()
        conexion.close()
        return {"error": "No hay campos para actualizar"}
    
    valores.append(id_producto)
    sql = f"UPDATE productos SET {', '.join(campos)} WHERE id_producto = %s"
    
    # Crear cursor dictionary para SELECT
    cursor_dict = conexion.cursor(dictionary=True)
    
    try:
        # Verificar primero que el producto existe
        cursor_dict.execute("SELECT id_producto FROM productos WHERE id_producto = %s", (id_producto,))
        producto_existe = cursor_dict.fetchone()
        
        if not producto_existe:
            cursor.close()
            cursor_dict.close()
            conexion.close()
            return {"error": f"Producto con ID {id_producto} no encontrado"}
        
        # Ejecutar el UPDATE
        cursor.execute(sql, valores)
        conexion.commit()
        filas_afectadas = cursor.rowcount
        
        # Si no se afectaron filas, puede ser que los valores sean iguales
        # Esto no es necesariamente un error - simplemente no había cambios
        if filas_afectadas == 0:
            # Verificar si los valores son realmente diferentes
            cursor_dict.execute("SELECT nombre, descripcion, precio, categoria, activo FROM productos WHERE id_producto = %s", (id_producto,))
            producto_actual = cursor_dict.fetchone()
            
            if producto_actual:
                # Comparar valores para ver si realmente hay cambios
                hay_cambios = False
                if producto.nombre is not None and producto.nombre != producto_actual.get('nombre'):
                    hay_cambios = True
                if producto.descripcion is not None and str(producto.descripcion) != str(producto_actual.get('descripcion', '')):
                    hay_cambios = True
                if producto.precio is not None and float(producto.precio) != float(producto_actual.get('precio', 0)):
                    hay_cambios = True
                if producto.categoria is not None and producto.categoria != producto_actual.get('categoria'):
                    hay_cambios = True
                if producto.activo is not None and bool(producto.activo) != bool(producto_actual.get('activo', False)):
                    hay_cambios = True
                
                if hay_cambios:
                    cursor.close()
                    cursor_dict.close()
                    conexion.close()
                    return {"error": f"No se pudo actualizar el producto con ID {id_producto}. Los valores pueden ser idénticos a los actuales."}
                else:
                    # No hay cambios, pero no es un error - el producto ya tiene esos valores
                    cursor.close()
                    cursor_dict.close()
                    conexion.close()
                    return {"message": "Producto actualizado correctamente (sin cambios en los campos básicos)", "sin_cambios": True}
        
        cursor.close()
        cursor_dict.close()
        conexion.close()
        return {"message": "Producto actualizado correctamente"}
    except Exception as e:
        conexion.rollback()
        cursor.close()
        cursor_dict.close()
        conexion.close()
        return {"error": f"Error al actualizar producto: {str(e)}"}

def eliminar_producto(id_producto: int):
    conexion = conectar()
    if not conexion:
        return {"error": "Error de conexión a la base de datos"}
    
    cursor = conexion.cursor()
    sql = "UPDATE productos SET activo = 0 WHERE id_producto = %s"
    
    try:
        cursor.execute(sql, (id_producto,))
        conexion.commit()
        if cursor.rowcount == 0:
            cursor.close()
            conexion.close()
            return {"error": "Producto no encontrado"}
        cursor.close()
        conexion.close()
        return {"message": "Producto desactivado correctamente"}
    except Exception as e:
        conexion.rollback()
        cursor.close()
        conexion.close()
        return {"error": f"Error al desactivar producto: {str(e)}"}

