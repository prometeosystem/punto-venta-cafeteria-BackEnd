from pydantic import BaseModel, EmailStr
from typing import Optional
from enum import Enum

class RolEnum(str, Enum):
    VENDEDOR = "vendedor"
    COCINA = "cocina"
    ADMINISTRADOR = "administrador"
    SUPERADMINISTRADOR = "superadministrador"

class UsuarioBase(BaseModel):
    nombre: str
    apellido_paterno: str
    apellido_materno: str
    correo: EmailStr
    contrasena: str
    celular: str
    rol: RolEnum
    activo: bool = True

class UsuarioCreate(UsuarioBase):
    pass

class UsuarioUpdate(BaseModel):
    nombre: Optional[str] = None
    apellido_paterno: Optional[str] = None
    apellido_materno: Optional[str] = None
    correo: Optional[EmailStr] = None
    celular: Optional[str] = None
    rol: Optional[RolEnum] = None
    activo: Optional[bool] = None

class UsuarioResponse(UsuarioBase):
    id_usuario: int
    
    class Config:
        from_attributes = True

class LoginSchema(BaseModel):
    correo: EmailStr
    contrasena: str
    
    class Config:
        json_schema_extra = {
            "example": {
                "correo": "vendedor@cafeteria.com",
                "contrasena": "password123"
            }
        }

