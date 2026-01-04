from repository.reporte_repository import (
    obtener_ventas_por_dia,
    obtener_productos_mas_vendidos,
    analizar_compras_recomendadas
)

def obtener_ventas_por_dia_service(fecha_inicio: str, fecha_fin: str):
    return obtener_ventas_por_dia(fecha_inicio, fecha_fin)

def obtener_productos_mas_vendidos_service(fecha_inicio: str, fecha_fin: str, limite: int = 10):
    return obtener_productos_mas_vendidos(fecha_inicio, fecha_fin, limite)

def analizar_compras_recomendadas_service(meses_analisis: int = 3):
    return analizar_compras_recomendadas(meses_analisis)

