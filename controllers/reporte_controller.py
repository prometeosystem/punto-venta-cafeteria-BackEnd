from fastapi import APIRouter, Depends, Query
from services.reporte_service import (
    obtener_ventas_por_dia_service,
    obtener_productos_mas_vendidos_service,
    analizar_compras_recomendadas_service
)
from utils.auth import get_current_user

router = APIRouter()

@router.get("/ventas_por_dia", summary="Obtener ventas agrupadas por día")
async def obtener_ventas_por_dia(
    fecha_inicio: str = Query(..., description="Fecha inicio en formato YYYY-MM-DD"),
    fecha_fin: str = Query(..., description="Fecha fin en formato YYYY-MM-DD"),
    current_user: dict = Depends(get_current_user)
):
    """
    Obtiene las ventas agrupadas por día para un período específico.
    
    Retorna:
    - fecha: Fecha del día
    - cantidad_ventas: Número de ventas ese día
    - total_ventas: Suma total de ventas
    - ticket_promedio: Promedio de ticket por venta
    """
    return obtener_ventas_por_dia_service(fecha_inicio, fecha_fin)

@router.get("/productos_mas_vendidos", summary="Obtener productos más vendidos")
async def obtener_productos_mas_vendidos(
    fecha_inicio: str = Query(..., description="Fecha inicio en formato YYYY-MM-DD"),
    fecha_fin: str = Query(..., description="Fecha fin en formato YYYY-MM-DD"),
    limite: int = Query(10, description="Número máximo de productos a retornar"),
    current_user: dict = Depends(get_current_user)
):
    """
    Obtiene los productos más vendidos en un período específico.
    
    Retorna:
    - id_producto: ID del producto
    - nombre: Nombre del producto
    - categoria: Categoría del producto
    - cantidad_vendida: Cantidad total vendida
    - total_ventas: Total en dinero de las ventas
    - veces_vendido: Número de veces que se vendió
    """
    return obtener_productos_mas_vendidos_service(fecha_inicio, fecha_fin, limite)

@router.get("/compras_recomendadas", summary="Análisis de compras recomendadas")
async def obtener_compras_recomendadas(
    meses_analisis: int = Query(3, description="Número de meses históricos a analizar"),
    current_user: dict = Depends(get_current_user)
):
    """
    Analiza el consumo histórico de insumos y genera recomendaciones de compra
    para el siguiente mes.
    
    El análisis considera:
    - Consumo histórico de los últimos N meses
    - Stock actual de cada insumo
    - Cantidad mínima requerida
    - Proyección de consumo del siguiente mes
    
    Retorna recomendaciones ordenadas por urgencia (alta, media, baja).
    """
    return analizar_compras_recomendadas_service(meses_analisis)

