from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from database.conexion import conectar

# Configuración de seguridad
SECRET_KEY = "tu_clave_secreta_muy_segura_cambiar_en_produccion"  # Cambiar en producción
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/login")

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verifica si la contraseña coincide con el hash
    
    Nota: Si la contraseña es más larga que 72 bytes, se trunca antes de verificar
    para mantener consistencia con get_password_hash.
    """
    try:
        # Truncar si es necesario (mismo límite que en get_password_hash)
        password_bytes = plain_password.encode('utf-8')
        if len(password_bytes) > 72:
            password_bytes = password_bytes[:72]
            plain_password = password_bytes.decode('utf-8', errors='ignore')
        
        return pwd_context.verify(plain_password, hashed_password)
    except Exception:
        # Fallback a bcrypt directo si passlib falla (compatibilidad)
        import bcrypt
        try:
            # Truncar también en el fallback
            password_bytes = plain_password.encode('utf-8')
            if len(password_bytes) > 72:
                password_bytes = password_bytes[:72]
            
            return bcrypt.checkpw(
                password_bytes, 
                hashed_password.encode('utf-8')
            )
        except Exception:
            return False

def get_password_hash(password: str) -> str:
    """Genera el hash de la contraseña
    
    La contraseña debe ser un string de 6-15 caracteres (ya validado antes de llegar aquí).
    """
    # Validaciones básicas
    if not password:
        raise ValueError("La contraseña no puede estar vacía")
    
    if not isinstance(password, str):
        raise ValueError(f"La contraseña debe ser un string. Tipo recibido: {type(password).__name__}")
    
    # Limpiar espacios
    password = password.strip()
    
    if not password:
        raise ValueError("La contraseña no puede estar vacía después de limpiar espacios")
    
    # Verificación de longitud
    if len(password) < 6:
        raise ValueError(f"La contraseña debe tener al menos 6 caracteres. Recibido: {len(password)} caracteres.")
    
    if len(password) > 15:
        raise ValueError(f"La contraseña no puede tener más de 15 caracteres. Recibido: {len(password)} caracteres.")
    
    # Verificar bytes (bcrypt tiene límite de 72 bytes)
    password_bytes = password.encode('utf-8')
    bytes_length = len(password_bytes)
    
    # Con 15 caracteres máximo, nunca debería exceder 72 bytes, pero verificamos
    if bytes_length > 72:
        # Truncar a 72 bytes si es necesario (no debería pasar)
        password_bytes = password_bytes[:72]
        password = password_bytes.decode('utf-8', errors='ignore')
        # Si después del truncamiento está vacía, error
        if not password:
            raise ValueError("Error: La contraseña quedó vacía después del procesamiento")
    
    # Intentar hashear con passlib
    try:
        print(f"[DEBUG get_password_hash] Hasheando contraseña: '{password}' (len={len(password)}, bytes={bytes_length})")
        hashed = pwd_context.hash(password)
        print(f"[DEBUG get_password_hash] Hash generado exitosamente")
        return hashed
    except ValueError as e:
        # Si es un ValueError de passlib/bcrypt, verificar si es por longitud
        error_msg = str(e).lower()
        print(f"[DEBUG get_password_hash] ValueError capturado: {error_msg}")
        if "longer" in error_msg or "72" in error_msg or "cannot be" in error_msg:
            # Intentar con bcrypt directamente como fallback
            try:
                import bcrypt
                print(f"[DEBUG get_password_hash] Intentando con bcrypt directamente...")
                salt = bcrypt.gensalt()
                hashed = bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')
                print(f"[DEBUG get_password_hash] Hash generado con bcrypt directamente")
                return hashed
            except Exception as bcrypt_error:
                raise ValueError(
                    f"Error al hashear la contraseña: {str(e)}. "
                    f"Fallback a bcrypt también falló: {str(bcrypt_error)}. "
                    f"Contraseña recibida: {len(password)} caracteres, {bytes_length} bytes. "
                    f"Valor: '{password}'"
                )
        raise
    except Exception as e:
        # Cualquier otro error - intentar con bcrypt directamente
        print(f"[DEBUG get_password_hash] Excepción capturada: {type(e).__name__}: {str(e)}")
        try:
            import bcrypt
            print(f"[DEBUG get_password_hash] Intentando fallback con bcrypt directamente...")
            salt = bcrypt.gensalt()
            hashed = bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')
            print(f"[DEBUG get_password_hash] Hash generado con bcrypt directamente (fallback)")
            return hashed
        except Exception as bcrypt_error:
            raise ValueError(
                f"Error inesperado al hashear la contraseña: {str(e)}. "
                f"Tipo: {type(e).__name__}. "
                f"Fallback a bcrypt también falló: {str(bcrypt_error)}. "
                f"Contraseña: {len(password)} caracteres, {bytes_length} bytes."
            )

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    """Crea un token JWT"""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def get_usuario_by_correo(correo: str):
    """Obtiene un usuario por su correo"""
    conexion = conectar()
    if not conexion:
        return None
    cursor = conexion.cursor(dictionary=True)
    sql = "SELECT * FROM usuarios WHERE correo = %s"
    cursor.execute(sql, (correo,))
    usuario = cursor.fetchone()
    cursor.close()
    conexion.close()
    return usuario

def authenticate_user(correo: str, password: str):
    """Autentica un usuario"""
    usuario = get_usuario_by_correo(correo)
    if not usuario:
        return False
    if not verify_password(password, usuario["contrasena"]):
        return False
    return usuario

async def get_current_user(token: str = Depends(oauth2_scheme)):
    """Obtiene el usuario actual desde el token"""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="No se pudieron validar las credenciales",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        correo: str = payload.get("sub")
        if correo is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    usuario = get_usuario_by_correo(correo)
    if usuario is None:
        raise credentials_exception
    return usuario

def require_role(allowed_roles: list):
    """Decorador para verificar roles"""
    async def role_checker(current_user: dict = Depends(get_current_user)):
        if current_user["rol"] not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="No tienes permisos suficientes"
            )
        return current_user
    return role_checker

