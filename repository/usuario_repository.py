from database.conexion import conectar
from utils.auth import get_password_hash
from schemas.usuario_schema import UsuarioCreate, UsuarioUpdate

def crear_usuario(usuario: UsuarioCreate):
    conexion = conectar()
    if not conexion:
        return {"error": "Error de conexión a la base de datos"}
    
    cursor = conexion.cursor()
    
    # Verificar si el correo ya existe
    sql_check = "SELECT id_usuario FROM usuarios WHERE correo = %s"
    cursor.execute(sql_check, (usuario.correo,))
    if cursor.fetchone():
        cursor.close()
        conexion.close()
        return {"error": "El correo ya está registrado"}
    
    # Hash de la contraseña
    contrasena_hash = get_password_hash(usuario.contrasena)
    
    sql = """
    INSERT INTO usuarios(
        nombre, apellido_paterno, apellido_materno, correo, 
        contrasena, celular, rol, activo
    )
    VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
    """
    datos = (
        usuario.nombre, usuario.apellido_paterno, usuario.apellido_materno,
        usuario.correo, contrasena_hash, usuario.celular, usuario.rol.value, usuario.activo
    )
    
    try:
        cursor.execute(sql, datos)
        conexion.commit()
        usuario_id = cursor.lastrowid
        cursor.close()
        conexion.close()
        return {"message": "Usuario creado correctamente", "id_usuario": usuario_id}
    except Exception as e:
        conexion.rollback()
        cursor.close()
        conexion.close()
        return {"error": f"Error al crear usuario: {str(e)}"}

def ver_todos_usuarios():
    conexion = conectar()
    if not conexion:
        return {"error": "Error de conexión a la base de datos"}
    
    cursor = conexion.cursor(dictionary=True)
    sql = "SELECT id_usuario, nombre, apellido_paterno, apellido_materno, correo, celular, rol, activo FROM usuarios"
    cursor.execute(sql)
    filas = cursor.fetchall()
    cursor.close()
    conexion.close()
    return filas

def ver_usuario_by_id(id_usuario: int):
    conexion = conectar()
    if not conexion:
        return {"error": "Error de conexión a la base de datos"}
    
    cursor = conexion.cursor(dictionary=True)
    sql = "SELECT id_usuario, nombre, apellido_paterno, apellido_materno, correo, celular, rol, activo FROM usuarios WHERE id_usuario = %s"
    cursor.execute(sql, (id_usuario,))
    usuario = cursor.fetchone()
    cursor.close()
    conexion.close()
    
    if not usuario:
        return {"error": "Usuario no encontrado"}
    return usuario

def editar_usuario(id_usuario: int, usuario: UsuarioUpdate):
    conexion = conectar()
    if not conexion:
        return {"error": "Error de conexión a la base de datos"}
    
    cursor = conexion.cursor()
    
    # Construir query dinámicamente
    campos = []
    valores = []
    
    if usuario.nombre is not None:
        campos.append("nombre = %s")
        valores.append(usuario.nombre)
    if usuario.apellido_paterno is not None:
        campos.append("apellido_paterno = %s")
        valores.append(usuario.apellido_paterno)
    if usuario.apellido_materno is not None:
        campos.append("apellido_materno = %s")
        valores.append(usuario.apellido_materno)
    if usuario.correo is not None:
        campos.append("correo = %s")
        valores.append(usuario.correo)
    if usuario.celular is not None:
        campos.append("celular = %s")
        valores.append(usuario.celular)
    if usuario.rol is not None:
        campos.append("rol = %s")
        valores.append(usuario.rol.value)
    if usuario.activo is not None:
        campos.append("activo = %s")
        valores.append(usuario.activo)
    
    if not campos:
        cursor.close()
        conexion.close()
        return {"error": "No hay campos para actualizar"}
    
    valores.append(id_usuario)
    sql = f"UPDATE usuarios SET {', '.join(campos)} WHERE id_usuario = %s"
    
    try:
        cursor.execute(sql, valores)
        conexion.commit()
        if cursor.rowcount == 0:
            cursor.close()
            conexion.close()
            return {"error": "Usuario no encontrado"}
        cursor.close()
        conexion.close()
        return {"message": "Usuario actualizado correctamente"}
    except Exception as e:
        conexion.rollback()
        cursor.close()
        conexion.close()
        return {"error": f"Error al actualizar usuario: {str(e)}"}

def eliminar_usuario(id_usuario: int):
    conexion = conectar()
    if not conexion:
        return {"error": "Error de conexión a la base de datos"}
    
    cursor = conexion.cursor()
    sql = "UPDATE usuarios SET activo = 0 WHERE id_usuario = %s"
    
    try:
        cursor.execute(sql, (id_usuario,))
        conexion.commit()
        if cursor.rowcount == 0:
            cursor.close()
            conexion.close()
            return {"error": "Usuario no encontrado"}
        cursor.close()
        conexion.close()
        return {"message": "Usuario desactivado correctamente"}
    except Exception as e:
        conexion.rollback()
        cursor.close()
        conexion.close()
        return {"error": f"Error al desactivar usuario: {str(e)}"}

