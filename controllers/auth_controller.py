from fastapi import APIRouter, Depends, HTTPException, status
from datetime import timedelta
from schemas.usuario_schema import LoginSchema
from utils.auth import authenticate_user, create_access_token, ACCESS_TOKEN_EXPIRE_MINUTES, get_current_user

router = APIRouter()

@router.post("/login", summary="Iniciar sesión", response_description="Token de acceso JWT")
async def login(login_data: LoginSchema):
    """
    Autenticación de usuario en el sistema.
    
    Retorna un token JWT que debe ser usado en el header `Authorization: Bearer <token>`
    para acceder a los endpoints protegidos.
    
    **Ejemplo de uso:**
    1. Realiza el login con correo/user y contraseña
    2. Copia el `access_token` de la respuesta
    3. Usa el botón "Authorize" en Swagger o incluye el header: `Authorization: Bearer <token>`
    """
    usuario = authenticate_user(login_data.correo_o_user, login_data.contrasena)
    if not usuario:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Correo/user o contraseña incorrectos",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    # Usamos el correo como sub en el token para mantener compatibilidad
    access_token = create_access_token(
        data={"sub": usuario["correo"], "rol": usuario["rol"]},
        expires_delta=access_token_expires
    )
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "usuario": {
            "id_usuario": usuario["id_usuario"],
            "nombre": usuario["nombre"],
            "correo": usuario["correo"],
            "user": usuario["user"],
            "rol": usuario["rol"]
        }
    }

@router.get("/me", summary="Información del usuario actual")
async def get_current_user_info(current_user: dict = Depends(get_current_user)):
    """
    Obtener información del usuario autenticado.
    
    Requiere autenticación. Retorna los datos del usuario que está actualmente logueado.
    """
    return {
        "id_usuario": current_user["id_usuario"],
        "nombre": current_user["nombre"],
        "apellido_paterno": current_user["apellido_paterno"],
        "apellido_materno": current_user["apellido_materno"],
        "correo": current_user["correo"],
        "user": current_user["user"],
        "rol": current_user["rol"],
        "activo": current_user["activo"]
    }

