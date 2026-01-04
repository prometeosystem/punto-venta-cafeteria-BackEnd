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
    
    # La contraseña ya debería estar validada por el schema, pero verificamos por seguridad
    contrasena = usuario.contrasena
    
    # Logging para debug
    print(f"[DEBUG] Tipo de contrasena en repositorio: {type(contrasena).__name__}")
    print(f"[DEBUG] Longitud de contrasena: {len(contrasena) if isinstance(contrasena, str) else 'N/A'}")
    print(f"[DEBUG] Valor de contrasena (primeros 20 chars): {str(contrasena)[:20] if contrasena else 'None'}")
    print(f"[DEBUG] Bytes de contrasena: {len(contrasena.encode('utf-8')) if isinstance(contrasena, str) else 'N/A'}")
    
    # Verificación final: debe ser string de 6-15 caracteres
    if not isinstance(contrasena, str):
        cursor.close()
        conexion.close()
        return {"error": f"Error: La contraseña debe ser un string. Tipo recibido: {type(contrasena).__name__}"}
    
    if len(contrasena) < 6:
        cursor.close()
        conexion.close()
        return {"error": f"Error: La contraseña debe tener al menos 6 caracteres. Recibido: {len(contrasena)} caracteres."}
    
    if len(contrasena) > 15:
        cursor.close()
        conexion.close()
        return {"error": f"Error: La contraseña no puede tener más de 15 caracteres. Recibido: {len(contrasena)} caracteres."}
    
    # Hash de la contraseña (ahora sabemos que es un string válido de 6-15 caracteres)
    try:
        print(f"[DEBUG] Llamando a get_password_hash con: '{contrasena}' (len={len(contrasena)}, bytes={len(contrasena.encode('utf-8'))})")
        contrasena_hash = get_password_hash(contrasena)
        print(f"[DEBUG] Hash generado exitosamente: {contrasena_hash[:50]}...")
    except Exception as e:
        print(f"[DEBUG] Error en get_password_hash: {type(e).__name__}: {str(e)}")
        cursor.close()
        conexion.close()
        return {"error": f"Error al procesar la contraseña: {str(e)}"}
    
    # Manejar apellido_materno None o vacío
    apellido_materno = usuario.apellido_materno if usuario.apellido_materno and usuario.apellido_materno.strip() else None
    
    # Manejar celular None o vacío
    celular = usuario.celular if usuario.celular and usuario.celular.strip() else None
    
    sql = """
    INSERT INTO usuarios(
        nombre, apellido_paterno, apellido_materno, correo, 
        contrasena, celular, rol, activo
    )
    VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
    """
    datos = (
        usuario.nombre, usuario.apellido_paterno, apellido_materno,
        usuario.correo, contrasena_hash, celular, usuario.rol.value, usuario.activo
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
    sql = """
    SELECT 
        id_usuario, 
        nombre, 
        apellido_paterno, 
        apellido_materno,
        CONCAT(nombre, ' ', apellido_paterno, IFNULL(CONCAT(' ', apellido_materno), '')) as nombre_completo,
        correo, 
        celular, 
        rol, 
        activo 
    FROM usuarios
    ORDER BY nombre, apellido_paterno
    """
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
    sql = """
    SELECT 
        id_usuario, 
        nombre, 
        apellido_paterno, 
        apellido_materno,
        CONCAT(nombre, ' ', apellido_paterno, IFNULL(CONCAT(' ', apellido_materno), '')) as nombre_completo,
        correo, 
        celular, 
        rol, 
        activo 
    FROM usuarios 
    WHERE id_usuario = %s
    """
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

def obtener_estadisticas_empleados():
    """Obtiene estadísticas de empleados: total activos y por rol"""
    conexion = conectar()
    if not conexion:
        return {"error": "Error de conexión a la base de datos"}
    
    cursor = conexion.cursor(dictionary=True)
    
    # Total de empleados activos
    sql_total = "SELECT COUNT(*) as total FROM usuarios WHERE activo = 1"
    cursor.execute(sql_total)
    total_activos = cursor.fetchone()["total"]
    
    # Empleados por rol (solo activos)
    sql_por_rol = """
    SELECT 
        rol,
        COUNT(*) as cantidad
    FROM usuarios 
    WHERE activo = 1
    GROUP BY rol
    """
    cursor.execute(sql_por_rol)
    por_rol = cursor.fetchall()
    
    # Convertir a diccionario más fácil de usar
    estadisticas_por_rol = {}
    for item in por_rol:
        estadisticas_por_rol[item["rol"]] = item["cantidad"]
    
    cursor.close()
    conexion.close()
    
    return {
        "total_empleados": total_activos,
        "vendedores": estadisticas_por_rol.get("vendedor", 0),
        "cocina": estadisticas_por_rol.get("cocina", 0),
        "administradores": estadisticas_por_rol.get("administrador", 0) + estadisticas_por_rol.get("superadministrador", 0)
    }

