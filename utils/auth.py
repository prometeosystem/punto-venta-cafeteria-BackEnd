import os

from datetime import datetime, timedelta

from typing import Optional

from jose import JWTError, jwt

from passlib.context import CryptContext

from fastapi import Depends, HTTPException, status

from fastapi.security import OAuth2PasswordBearer

from database.conexion import conectar

from dotenv import load_dotenv



# Cargar variables de entorno desde el archivo .env

load_dotenv()



# ============================================

# Configuración de seguridad (Variables de Entorno)

# ============================================

# Se usa os.getenv para obtener los valores del archivo .env

SECRET_KEY = os.getenv("SECRET_KEY", "clave_temporal_no_usar_en_produccion")

ALGORITHM = os.getenv("ALGORITHM", "HS256")

# Convertimos a entero porque las variables de entorno siempre llegan como texto

ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", 30))



pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/login")



def verify_password(plain_password: str, hashed_password: str) -> bool:

    """Verifica si la contraseña coincide con el hash"""

    try:

        password_bytes = plain_password.encode('utf-8')

        if len(password_bytes) > 72:

            password_bytes = password_bytes[:72]

            plain_password = password_bytes.decode('utf-8', errors='ignore')

        

        return pwd_context.verify(plain_password, hashed_password)

    except Exception:

        import bcrypt

        try:

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

    """Genera el hash de la contraseña"""

    if not password:

        raise ValueError("La contraseña no puede estar vacía")

    

    password = password.strip()

    

    # Bcrypt tiene un límite físico de 72 bytes

    password_bytes = password.encode('utf-8')

    if len(password_bytes) > 72:

        password_bytes = password_bytes[:72]

        password = password_bytes.decode('utf-8', errors='ignore')

    

    return pwd_context.hash(password)



def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):

    """Crea un token JWT usando la SECRET_KEY del servidor"""

    to_encode = data.copy()

    if expires_delta:

        expire = datetime.utcnow() + expires_delta

    else:

        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)

    

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

    """Autentica un usuario verificando correo y password"""

    usuario = get_usuario_by_correo(correo)

    if not usuario:

        return False

    if not verify_password(password, usuario["contrasena"]):

        return False

    return usuario



async def get_current_user(token: str = Depends(oauth2_scheme)):

    """Obtiene el usuario actual desde el token JWT"""

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

    """Filtro de seguridad por roles (Admin, Mesero, etc.)"""

    async def role_checker(current_user: dict = Depends(get_current_user)):

        if current_user["rol"] not in allowed_roles:

            raise HTTPException(

                status_code=status.HTTP_403_FORBIDDEN,

                detail="No tienes permisos suficientes"

            )

        return current_user

    return role_checker
