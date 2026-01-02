from database.conexion import conectar
from schemas.cliente_schema import VisitaClienteCreate
from utils.auth import get_password_hash
from datetime import datetime

def crear_cliente(cliente):
    conexion = conectar()
    if not conexion:
        return {"error": "Error de conexión a la base de datos"}
    
    cursor = conexion.cursor()
    
    # Verificar si el correo ya existe
    sql_check = "SELECT id_cliente FROM clientes WHERE correo = %s"
    cursor.execute(sql_check, (cliente.correo,))
    if cursor.fetchone():
        cursor.close()
        conexion.close()
        return {"error": "El correo ya está registrado"}
    
    # Hash de la contraseña
    contrasena_hash = get_password_hash(cliente.contrasena)
    
    sql = """
    INSERT INTO clientes(
        nombre, apellido_paterno, apellido_materno, correo, contrasena, 
        celular, rfc, direccion, puntos
    )
    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
    """
    datos = (
        cliente.nombre, cliente.apellido_paterno, cliente.apellido_materno,
        cliente.correo, contrasena_hash, cliente.celular,
        cliente.rfc, cliente.direccion, cliente.puntos
    )
    
    try:
        cursor.execute(sql, datos)
        conexion.commit()
        cliente_id = cursor.lastrowid
        cursor.close()
        conexion.close()
        return {"message": "Cliente creado correctamente", "id_cliente": cliente_id}
    except Exception as e:
        conexion.rollback()
        cursor.close()
        conexion.close()
        return {"error": f"Error al crear cliente: {str(e)}"}

def ver_todos_clientes():
    conexion = conectar()
    if not conexion:
        return {"error": "Error de conexión a la base de datos"}
    
    cursor = conexion.cursor(dictionary=True)
    sql = "SELECT id_cliente, nombre, apellido_paterno, apellido_materno, correo, celular, rfc, direccion, puntos FROM clientes"
    cursor.execute(sql)
    resultados = cursor.fetchall()
    cursor.close()
    conexion.close()
    return resultados

def ver_cliente_by_id(id_cliente: int):
    conexion = conectar()
    if not conexion:
        return {"error": "Error de conexión a la base de datos"}
    
    cursor = conexion.cursor(dictionary=True)
    sql = "SELECT id_cliente, nombre, apellido_paterno, apellido_materno, correo, celular, rfc, direccion, puntos FROM clientes WHERE id_cliente = %s"
    cursor.execute(sql, (id_cliente,))
    cliente = cursor.fetchone()
    cursor.close()
    conexion.close()
    
    if not cliente:
        return {"error": "Cliente no encontrado"}
    return cliente



def editar_cliente(id_cliente: int, cliente):
    conexion = conectar()
    if not conexion:
        return {"error": "Error de conexión a la base de datos"}
    
    cursor = conexion.cursor()
    
    # Construir query dinámicamente
    campos = []
    valores = []
    
    if cliente.nombre is not None:
        campos.append("nombre = %s")
        valores.append(cliente.nombre)
    if cliente.apellido_paterno is not None:
        campos.append("apellido_paterno = %s")
        valores.append(cliente.apellido_paterno)
    if cliente.apellido_materno is not None:
        campos.append("apellido_materno = %s")
        valores.append(cliente.apellido_materno)
    if cliente.correo is not None:
        campos.append("correo = %s")
        valores.append(cliente.correo)
    if cliente.contrasena is not None:
        campos.append("contrasena = %s")
        valores.append(get_password_hash(cliente.contrasena))
    if cliente.celular is not None:
        campos.append("celular = %s")
        valores.append(cliente.celular)
    if cliente.rfc is not None:
        campos.append("rfc = %s")
        valores.append(cliente.rfc)
    if cliente.direccion is not None:
        campos.append("direccion = %s")
        valores.append(cliente.direccion)
    if cliente.puntos is not None:
        campos.append("puntos = %s")
        valores.append(cliente.puntos)
    
    if not campos:
        cursor.close()
        conexion.close()
        return {"error": "No hay campos para actualizar"}
    
    valores.append(id_cliente)
    sql = f"UPDATE clientes SET {', '.join(campos)} WHERE id_cliente = %s"
    
    try:
        cursor.execute(sql, valores)
        conexion.commit()
        if cursor.rowcount == 0:
            cursor.close()
            conexion.close()
            return {"error": "Cliente no encontrado"}
        cursor.close()
        conexion.close()
        return {"message": "Cliente actualizado correctamente"}
    except Exception as e:
        conexion.rollback()
        cursor.close()
        conexion.close()
        return {"error": f"Error al actualizar cliente: {str(e)}"}

def registrar_visita(visita: VisitaClienteCreate):
    """Registra una visita de un cliente"""
    conexion = conectar()
    if not conexion:
        return {"error": "Error de conexión a la base de datos"}
    
    cursor = conexion.cursor()
    sql = """
    INSERT INTO visitas_clientes(id_cliente, id_venta, fecha_visita)
    VALUES (%s, %s, %s)
    """
    datos = (visita.id_cliente, visita.id_venta, visita.fecha_visita)
    
    try:
        cursor.execute(sql, datos)
        conexion.commit()
        visita_id = cursor.lastrowid
        cursor.close()
        conexion.close()
        return {"message": "Visita registrada correctamente", "id_visita": visita_id}
    except Exception as e:
        conexion.rollback()
        cursor.close()
        conexion.close()
        return {"error": f"Error al registrar visita: {str(e)}"}

def ver_visitas_cliente(id_cliente: int):
    """Obtiene todas las visitas de un cliente"""
    conexion = conectar()
    if not conexion:
        return {"error": "Error de conexión a la base de datos"}
    
    cursor = conexion.cursor(dictionary=True)
    sql = """
    SELECT v.*, ve.total, ve.fecha_venta
    FROM visitas_clientes v
    JOIN ventas ve ON v.id_venta = ve.id_venta
    WHERE v.id_cliente = %s
    ORDER BY v.fecha_visita DESC
    """
    cursor.execute(sql, (id_cliente,))
    visitas = cursor.fetchall()
    cursor.close()
    conexion.close()
    return visitas

def contar_visitas_cliente(id_cliente: int):
    """Cuenta el total de visitas de un cliente"""
    conexion = conectar()
    if not conexion:
        return {"error": "Error de conexión a la base de datos"}
    
    cursor = conexion.cursor()
    sql = "SELECT COUNT(*) as total FROM visitas_clientes WHERE id_cliente = %s"
    cursor.execute(sql, (id_cliente,))
    resultado = cursor.fetchone()
    cursor.close()
    conexion.close()
    return {"total_visitas": resultado[0] if resultado else 0}
