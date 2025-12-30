from database.conexion import conectar
from schemas.producto_schema import ProductoCreate, ProductoUpdate

def crear_producto(producto: ProductoCreate):
    conexion = conectar()
    if not conexion:
        return {"error": "Error de conexión a la base de datos"}
    
    cursor = conexion.cursor()
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
    sql = "SELECT * FROM productos WHERE activo = 1"
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
    sql = "SELECT * FROM productos WHERE id_producto = %s"
    cursor.execute(sql, (id_producto,))
    producto = cursor.fetchone()
    cursor.close()
    conexion.close()
    
    if not producto:
        return {"error": "Producto no encontrado"}
    return producto

def editar_producto(id_producto: int, producto: ProductoUpdate):
    conexion = conectar()
    if not conexion:
        return {"error": "Error de conexión a la base de datos"}
    
    cursor = conexion.cursor()
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
    
    if not campos:
        cursor.close()
        conexion.close()
        return {"error": "No hay campos para actualizar"}
    
    valores.append(id_producto)
    sql = f"UPDATE productos SET {', '.join(campos)} WHERE id_producto = %s"
    
    try:
        cursor.execute(sql, valores)
        conexion.commit()
        if cursor.rowcount == 0:
            cursor.close()
            conexion.close()
            return {"error": "Producto no encontrado"}
        cursor.close()
        conexion.close()
        return {"message": "Producto actualizado correctamente"}
    except Exception as e:
        conexion.rollback()
        cursor.close()
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

