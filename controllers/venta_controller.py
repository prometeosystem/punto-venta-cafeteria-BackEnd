from fastapi import APIRouter, Depends, Query
from schemas.venta_schema import VentaCreate
from services.venta_service import (
    crear_venta_service,
    ver_venta_by_id_service,
    ver_todas_ventas_service,
    ver_ventas_por_fecha_service,
    obtener_info_ticket_actual_service
)
from utils.auth import require_role, get_current_user

router = APIRouter()

@router.post("/crear_venta", summary="Crear nueva venta", response_description="ID de la venta creada")
async def crear_venta(
    venta: VentaCreate,
    current_user: dict = Depends(require_role(["vendedor", "administrador", "superadministrador"]))
):
    """
    Crear una nueva venta en el punto de venta.
    
    **Permisos requeridos:** Vendedor, Administrador o Superadministrador
    
    **Notas:**
    - El campo `id_cliente` es opcional (venta sin cliente registrado)
    - El `total` debe coincidir con la suma de los subtotales de los detalles
    - Cada detalle debe incluir: `id_producto`, `cantidad`, `precio_unitario`, `subtotal`
    """
    return crear_venta_service(venta)

@router.get("/ver_venta/{id_venta}", summary="Ver venta específica")
async def ver_venta_by_id(
    id_venta: int,
    current_user: dict = Depends(get_current_user)
):
    """
    Obtener los detalles completos de una venta específica.
    
    Incluye todos los detalles de productos vendidos.
    """
    return ver_venta_by_id_service(id_venta)

@router.get("/ver_ventas", summary="Listar ventas")
async def listar_ventas(
    fecha_inicio: str = Query(None, description="Fecha inicio en formato YYYY-MM-DD", examples=["2024-01-01"]),
    fecha_fin: str = Query(None, description="Fecha fin en formato YYYY-MM-DD", examples=["2024-01-31"]),
    current_user: dict = Depends(get_current_user)
):
    """
    Listar todas las ventas o filtrar por rango de fechas.
    
    **Parámetros opcionales:**
    - `fecha_inicio`: Fecha de inicio del rango (YYYY-MM-DD)
    - `fecha_fin`: Fecha de fin del rango (YYYY-MM-DD)
    
    Si se proporcionan ambas fechas, se filtran las ventas en ese rango.
    Si no se proporcionan, se retornan todas las ventas.
    """
    if fecha_inicio and fecha_fin:
        return ver_ventas_por_fecha_service(fecha_inicio, fecha_fin)
    return ver_todas_ventas_service()

@router.get("/info_ticket_actual", summary="Obtener información del ticket actual")
async def obtener_info_ticket_actual(
    current_user: dict = Depends(get_current_user)
):
    """
    Obtiene información sobre el ticket actual en el punto de venta.
    
    Retorna:
    - `ultimo_ticket_id`: Último ticket_id generado
    - `tickets_hoy`: Cantidad de tickets generados hoy
    - `siguiente_ticket_id`: Preview del siguiente ticket_id que se generará
    - `fecha_actual`: Fecha actual
    
    **Permisos requeridos:** Cualquier usuario autenticado
    """
    return obtener_info_ticket_actual_service()

