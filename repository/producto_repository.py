from database.conexion import conectar
from schemas.producto_schema import ProductoCreate, ProductoUpdate
from utils.normalize import normalizar_nombre
from decimal import Decimal

def crear_producto(producto: ProductoCreate):
    conexion = conectar()
    if not conexion:
        return {"error": "Error de conexión a la base de datos"}
    
    cursor = conexion.cursor()
    
    try:
        # Crear el producto
        sql = """
        INSERT INTO productos(nombre, descripcion, precio, categoria, tiempo_preparacion, activo)
        VALUES (%s, %s, %s, %s, %s, %s)
        """
        datos = (
            producto.nombre, producto.descripcion, producto.precio,
            producto.categoria, producto.tiempo_preparacion, producto.activo
        )
        cursor.execute(sql, datos)
        producto_id = cursor.lastrowid
        
        # Agregar insumos si se proporcionaron
        insumos_creados = []
        insumos_existentes = []
        errores = []
        
        if producto.insumos:
            for insumo_receta in producto.insumos:
                # Buscar insumo existente en la misma transacción
                nombre_normalizado_insumo = normalizar_nombre(insumo_receta.nombre_insumo)
                sql_buscar = "SELECT * FROM insumos WHERE nombre_normalizado = %s AND activo = 1"
                cursor.execute(sql_buscar, (nombre_normalizado_insumo,))
                insumo_encontrado = cursor.fetchone()
                
                if insumo_encontrado:
                    # Verificar que la unidad de medida coincida
                    if insumo_encontrado["unidad_medida"] != insumo_receta.unidad_medida:
                        errores.append(
                            f"El insumo '{insumo_receta.nombre_insumo}' existe pero con unidad de medida "
                            f"'{insumo_encontrado['unidad_medida']}', no '{insumo_receta.unidad_medida}'"
                        )
                        continue
                    
                    id_insumo = insumo_encontrado["id_insumo"]
                    insumos_existentes.append(insumo_receta.nombre_insumo)
                elif insumo_receta.crear_si_no_existe:
                    # Crear nuevo insumo en la misma transacción
                    try:
                        nombre_normalizado = normalizar_nombre(insumo_receta.nombre_insumo)
                        
                        # Verificar que no exista ya
                        sql_check_insumo = "SELECT id_insumo FROM insumos WHERE nombre_normalizado = %s"
                        cursor.execute(sql_check_insumo, (nombre_normalizado,))
                        if cursor.fetchone():
                            errores.append(f"El insumo '{insumo_receta.nombre_insumo}' ya existe")
                            continue
                        
                        # Insertar nuevo insumo
                        sql_crear_insumo = """
                        INSERT INTO insumos(
                            nombre, nombre_normalizado, descripcion, unidad_medida,
                            cantidad_actual, cantidad_minima, precio_compra, activo
                        )
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                        """
                        datos_insumo = (
                            insumo_receta.nombre_insumo,
                            nombre_normalizado,
                            insumo_receta.descripcion,
                            insumo_receta.unidad_medida,
                            insumo_receta.cantidad_actual or Decimal(0),
                            insumo_receta.cantidad_minima or Decimal(0),
                            insumo_receta.precio_compra or Decimal(0),
                            True
                        )
                        cursor.execute(sql_crear_insumo, datos_insumo)
                        id_insumo = cursor.lastrowid
                        insumos_creados.append(insumo_receta.nombre_insumo)
                    except Exception as e:
                        errores.append(f"Error al crear insumo '{insumo_receta.nombre_insumo}': {str(e)}")
                        continue
                else:
                    errores.append(
                        f"El insumo '{insumo_receta.nombre_insumo}' no existe. "
                        "Establece 'crear_si_no_existe: true' para crearlo automáticamente."
                    )
                    continue
                
                # Insertar en recetas_insumos (si ya existe, actualizar cantidad)
                sql_receta = """
                INSERT INTO recetas_insumos(id_producto, id_insumo, cantidad_necesaria)
                VALUES (%s, %s, %s)
                ON DUPLICATE KEY UPDATE cantidad_necesaria = VALUES(cantidad_necesaria)
                """
                try:
                    cursor.execute(sql_receta, (producto_id, id_insumo, insumo_receta.cantidad_necesaria))
                except Exception as e:
                    errores.append(f"Error al agregar insumo '{insumo_receta.nombre_insumo}': {str(e)}")
                    continue
        
        conexion.commit()
        cursor.close()
        conexion.close()
        
        respuesta = {
            "message": "Producto creado correctamente",
            "id_producto": producto_id,
            "insumos_agregados": len(producto.insumos) if producto.insumos else 0
        }
        
        if insumos_creados:
            respuesta["insumos_creados"] = insumos_creados
        if insumos_existentes:
            respuesta["insumos_existentes"] = insumos_existentes
        if errores:
            respuesta["errores"] = errores
        
        return respuesta
        
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
    
    if not producto:
        cursor.close()
        conexion.close()
        return {"error": "Producto no encontrado"}
    
    # Obtener insumos de la receta
    sql_receta = """
    SELECT r.id_receta, r.id_insumo, r.cantidad_necesaria, 
           i.nombre as insumo_nombre, i.unidad_medida
    FROM recetas_insumos r
    JOIN insumos i ON r.id_insumo = i.id_insumo
    WHERE r.id_producto = %s
    """
    cursor.execute(sql_receta, (id_producto,))
    insumos = cursor.fetchall()
    producto["insumos"] = insumos
    
    cursor.close()
    conexion.close()
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
    if producto.tiempo_preparacion is not None:
        campos.append("tiempo_preparacion = %s")
        valores.append(producto.tiempo_preparacion)
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

