"""
Utilidades para normalizar nombres de insumos y manejar unidades de medida
"""
import unicodedata
import re
from enum import Enum

class UnidadMedidaEnum(str, Enum):
    """Unidades de medida comunes para cocina"""
    # Peso
    GRAMOS = "gramos"
    KILOGRAMOS = "kilogramos"
    ONZAS = "onzas"
    LIBRAS = "libras"
    
    # Volumen
    MILILITROS = "mililitros"
    LITROS = "litros"
    TAZAS = "tazas"
    CUCHARADAS = "cucharadas"
    CUCHARADITAS = "cucharaditas"
    
    # Cantidad
    PIEZAS = "piezas"
    UNIDADES = "unidades"
    PAQUETES = "paquetes"
    LATAS = "latas"
    BOTELLAS = "botellas"

def normalizar_nombre(nombre: str) -> str:
    """
    Normaliza un nombre removiendo acentos, convirtiendo a minúsculas
    y eliminando espacios extra.
    
    Ejemplo: "Azúcar" -> "azucar", "Café molido" -> "cafe molido"
    """
    # Remover acentos y caracteres especiales
    nombre = unicodedata.normalize('NFD', nombre)
    nombre = ''.join(c for c in nombre if unicodedata.category(c) != 'Mn')
    
    # Convertir a minúsculas
    nombre = nombre.lower()
    
    # Eliminar espacios extra y espacios al inicio/final
    nombre = re.sub(r'\s+', ' ', nombre).strip()
    
    return nombre


