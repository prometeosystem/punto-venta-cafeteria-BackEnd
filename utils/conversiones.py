"""
Utilidades para conversión de unidades de medida
"""
from decimal import Decimal

# Factores de conversión a unidades base
FACTORES_CONVERSION = {
    # Masa
    'kg': Decimal('1000'),      # 1 kg = 1000 gramos
    'kilogramos': Decimal('1000'),  # Alias para kg
    'kilogramo': Decimal('1000'),   # Singular
    'gramos': Decimal('1'),    # Unidad base
    'gramo': Decimal('1'),     # Singular
    'onzas': Decimal('28.3495'),  # 1 onza = 28.3495 gramos
    'onza': Decimal('28.3495'),    # Singular
    
    # Volumen
    'litros': Decimal('1000'),     # 1 litro = 1000 mililitros
    'litro': Decimal('1000'),      # Singular
    'mililitros': Decimal('1'),    # Unidad base
    'mililitro': Decimal('1'),     # Singular
    'ml': Decimal('1'),            # Abreviación
    'onzas_fluidas': Decimal('29.5735'),  # 1 onza fluida = 29.5735 ml
    'onza_fluida': Decimal('29.5735'),    # Singular
    
    # Unidades
    'unidades': Decimal('1'),
    'unidad': Decimal('1'),        # Singular
    'piezas': Decimal('1'),
    'pieza': Decimal('1'),          # Singular
}

def convertir_a_unidad_base(cantidad: Decimal, unidad: str) -> Decimal:
    """
    Convierte una cantidad a su unidad base
    
    Masa: gramos (base)
    Volumen: mililitros (base)
    Unidades: unidades (base)
    """
    unidad_lower = unidad.lower().strip()
    
    if unidad_lower in FACTORES_CONVERSION:
        return cantidad * FACTORES_CONVERSION[unidad_lower]
    
    # Si no está en la lista, asumir que es 1:1 (unidades, piezas, etc.)
    return cantidad

def convertir_desde_unidad_base(cantidad_base: Decimal, unidad_destino: str) -> Decimal:
    """
    Convierte una cantidad desde la unidad base a la unidad destino
    """
    unidad_lower = unidad_destino.lower().strip()
    
    if unidad_lower in FACTORES_CONVERSION:
        factor = FACTORES_CONVERSION[unidad_lower]
        if factor > 0:
            return cantidad_base / factor
    
    # Si no está en la lista, asumir que es 1:1
    return cantidad_base

def convertir_unidades(cantidad: Decimal, unidad_origen: str, unidad_destino: str) -> Decimal:
    """
    Convierte una cantidad de una unidad a otra
    
    Ejemplos:
    - convertir_unidades(1, 'litros', 'mililitros') -> 1000
    - convertir_unidades(1000, 'gramos', 'kg') -> 1
    - convertir_unidades(250, 'mililitros', 'litros') -> 0.25
    """
    if unidad_origen.lower().strip() == unidad_destino.lower().strip():
        return cantidad
    
    # Convertir a unidad base
    cantidad_base = convertir_a_unidad_base(cantidad, unidad_origen)
    
    # Convertir desde unidad base a destino
    cantidad_destino = convertir_desde_unidad_base(cantidad_base, unidad_destino)
    
    return cantidad_destino

def son_unidades_compatibles(unidad1: str, unidad2: str) -> bool:
    """
    Verifica si dos unidades son compatibles (misma categoría: masa, volumen, unidades)
    """
    unidad1_lower = unidad1.lower().strip()
    unidad2_lower = unidad2.lower().strip()
    
    # Masa
    masa = ['kg', 'gramos', 'onzas']
    # Volumen
    volumen = ['litros', 'mililitros', 'onzas_fluidas']
    # Unidades
    unidades = ['unidades', 'piezas']
    
    categorias = [masa, volumen, unidades]
    
    for categoria in categorias:
        if unidad1_lower in categoria and unidad2_lower in categoria:
            return True
    
    # Si no están en ninguna categoría conocida, asumir compatibles
    return True

