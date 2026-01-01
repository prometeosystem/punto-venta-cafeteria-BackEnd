from pydantic import BaseModel, EmailStr, field_validator
from typing import Optional
from enum import Enum
import re

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
    user: str
    contrasena: str
    celular: str
    rol: RolEnum
    activo: bool = True
    
    @field_validator('user')
    @classmethod
    def validate_user(cls, v: str) -> str:
        """Valida que el campo user solo contenga letras y números"""
        if not re.match(r'^[a-zA-Z0-9]+$', v):
            raise ValueError('El campo user solo puede contener letras y números')
        if len(v) < 3:
            raise ValueError('El campo user debe tener al menos 3 caracteres')
        if len(v) > 100:
            raise ValueError('El campo user no puede tener más de 100 caracteres')
        return v

class UsuarioCreate(UsuarioBase):
    pass

class UsuarioUpdate(BaseModel):
    nombre: Optional[str] = None
    apellido_paterno: Optional[str] = None
    apellido_materno: Optional[str] = None
    correo: Optional[EmailStr] = None
    user: Optional[str] = None
    celular: Optional[str] = None
    rol: Optional[RolEnum] = None
    activo: Optional[bool] = None
    
    @field_validator('user')
    @classmethod
    def validate_user(cls, v: Optional[str]) -> Optional[str]:
        """Valida que el campo user solo contenga letras y números"""
        if v is None:
            return v
        if not re.match(r'^[a-zA-Z0-9]+$', v):
            raise ValueError('El campo user solo puede contener letras y números')
        if len(v) < 3:
            raise ValueError('El campo user debe tener al menos 3 caracteres')
        if len(v) > 100:
            raise ValueError('El campo user no puede tener más de 100 caracteres')
        return v

class UsuarioResponse(UsuarioBase):
    id_usuario: int
    
    class Config:
        from_attributes = True

class LoginSchema(BaseModel):
    correo_o_user: str
    contrasena: str
    
    class Config:
        json_schema_extra = {
            "example": {
                "correo_o_user": "vendedor@cafeteria.com o usuario123",
                "contrasena": "password123"
            }
        }

