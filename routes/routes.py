from fastapi import APIRouter
from controllers.cliente_controller import router as cliente_router
from controllers.usuario_controller import router as usuario_router
from controllers.auth_controller import router as auth_router
from controllers.producto_controller import router as producto_router
from controllers.inventario_controller import router as inventario_router
from controllers.venta_controller import router as venta_router
from controllers.comanda_controller import router as comanda_router
from controllers.receta_controller import router as receta_router
# TODO: Descomentar cuando se configure la integración con Loyabit
# from controllers.loyabit_controller import router as loyabit_router

api_router = APIRouter()

# Rutas de autenticación
api_router.include_router(auth_router, prefix="/api", tags=["Autenticación"])

# Rutas de clientes
api_router.include_router(cliente_router, prefix="/api/clientes", tags=["Clientes"])

# Rutas de usuarios/empleados
api_router.include_router(usuario_router, prefix="/api/usuarios", tags=["Usuarios"])

# Rutas de productos
api_router.include_router(producto_router, prefix="/api/productos", tags=["Productos"])

# Rutas de inventario
api_router.include_router(inventario_router, prefix="/api/inventario", tags=["Inventario"])

# Rutas de ventas
api_router.include_router(venta_router, prefix="/api/ventas", tags=["Ventas"])

# Rutas de comandas
api_router.include_router(comanda_router, prefix="/api/comandas", tags=["Comandas"])

# Rutas de recetas
api_router.include_router(receta_router, prefix="/api/recetas", tags=["Recetas"])

# TODO: Descomentar cuando se configure la integración con Loyabit
# Ver README_LOYABIT.md para instrucciones de configuración
# Rutas de integración con Loyabit
# api_router.include_router(loyabit_router, prefix="/api/loyabit", tags=["Loyabit"])