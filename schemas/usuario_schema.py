from pydantic import BaseModel, EmailStr, Field, field_validator, model_validator
from typing import Optional, Any
from enum import Enum

class RolEnum(str, Enum):
    VENDEDOR = "vendedor"
    COCINA = "cocina"
    ADMINISTRADOR = "administrador"
    SUPERADMINISTRADOR = "superadministrador"

class UsuarioBase(BaseModel):
    nombre: str
    apellido_paterno: str
    apellido_materno: Optional[str] = None
    correo: EmailStr
    contrasena: Any = Field(..., description="Contraseña entre 6 y 15 caracteres")
    celular: Optional[str] = None
    rol: RolEnum
    activo: bool = True
    
    @model_validator(mode='before')
    @classmethod
    def procesar_contrasena_antes(cls, data: Any) -> Any:
        """Procesa la contraseña ANTES de que Pydantic intente validar el tipo"""
        if isinstance(data, dict) and 'contrasena' in data:
            contrasena_value = data['contrasena']
            password_str = None
            
            # Si es un diccionario/objeto, extraer el valor
            if isinstance(contrasena_value, dict):
                # Intentar obtener valorCompleto primero (es el campo más común)
                password_str = contrasena_value.get('valorCompleto')
                
                # Si no está, buscar otros campos comunes
                if not password_str:
                    password_str = contrasena_value.get('valor') or contrasena_value.get('password') or contrasena_value.get('contrasena')
                
                # Si aún no hay valor, buscar el primer string válido (6-15 caracteres)
                if not password_str:
                    for key, value in contrasena_value.items():
                        if isinstance(value, str) and 6 <= len(value) <= 15:
                            password_str = value
                            break
                
                # Si encontramos un valor, reemplazarlo
                if password_str:
                    data['contrasena'] = password_str
                else:
                    raise ValueError('La contraseña debe ser un string de 6-15 caracteres. Envía solo el texto (ej: "1234567890"), no un objeto.')
            # Si es un string, verificar que tenga la longitud correcta
            elif isinstance(contrasena_value, str):
                if len(contrasena_value) < 6:
                    raise ValueError('La contraseña debe tener al menos 6 caracteres')
                if len(contrasena_value) > 15:
                    raise ValueError('La contraseña no puede tener más de 15 caracteres')
            # Si es otro tipo, convertir a string y verificar
            else:
                password_str = str(contrasena_value)
                # Si es muy largo, probablemente es un objeto convertido
                if len(password_str) > 50 or '{' in password_str or ':' in password_str:
                    raise ValueError('La contraseña debe ser un string simple de 6-15 caracteres. No envíes objetos.')
                # Si tiene longitud válida, usarlo
                if 6 <= len(password_str) <= 15:
                    data['contrasena'] = password_str
                else:
                    raise ValueError(f'La contraseña debe tener entre 6 y 15 caracteres. Recibido: {len(password_str)} caracteres.')
        
        return data
    
    @field_validator('contrasena', mode='after')
    @classmethod
    def validar_contrasena(cls, v: Any) -> str:
        """Valida la contraseña después de la extracción - debe ser string de 6-15 caracteres"""
        # Si aún es un dict (no se procesó correctamente), intentar extraer
        if isinstance(v, dict):
            v = v.get('valorCompleto') or v.get('valor') or v.get('password') or v.get('contrasena')
            if not v:
                raise ValueError('La contraseña debe ser un string, no un objeto.')
        
        # Convertir a string si no lo es
        if not isinstance(v, str):
            v = str(v)
            # Si es muy largo o parece objeto, rechazar
            if len(v) > 50 or '{' in v or ':' in v:
                raise ValueError('La contraseña debe ser un string simple de 6-15 caracteres. No envíes objetos.')
        
        # Validar longitud estricta
        if len(v) < 6:
            raise ValueError('La contraseña debe tener al menos 6 caracteres')
        if len(v) > 15:
            raise ValueError(f'La contraseña no puede tener más de 15 caracteres. Recibido: {len(v)} caracteres.')
        
        return v

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

