from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from routes.routes import api_router
from database.init_db import init_database

# Inicializar base de datos al arrancar (similar a Spring Boot ddl-auto=update)
print("🔄 Inicializando base de datos...")
init_database()

# Configuración de metadatos para Swagger
description = """
## Sistema de Control Inteligente - API para Cafetería ☕

API REST desarrollada con FastAPI para la gestión integral de una cafetería.

### Características principales:

* **Sistema de Autenticación y Roles**: Vendedor, Cocina, Administrador, Superadministrador
* **Punto de Venta**: Registro de ventas con múltiples métodos de pago
* **Sistema de Comandas**: Gestión de órdenes con estados (pendiente, en preparación, terminada)
* **Inventario Automático**: Resta automática de insumos cuando una comanda se marca como terminada
* **Gestión de Clientes**: Registro de visitas para tarjeta de fidelidad
* **Gestión de Productos e Insumos**: Control completo de productos y recetas

### Autenticación:

La mayoría de los endpoints requieren autenticación mediante JWT. 
1. Primero debes hacer login en `/api/login`
2. Copia el `access_token` del response
3. Haz clic en el botón **"Authorize"** 🔒 arriba a la derecha
4. Ingresa: `Bearer <tu_access_token>` (sin los corchetes)
5. Ahora podrás acceder a los endpoints protegidos

### Roles y Permisos:

* **Vendedor**: Puede crear ventas y comandas
* **Cocina**: Puede ver y actualizar estados de comandas
* **Administrador**: Gestión completa excepto usuarios
* **Superadministrador**: Acceso total al sistema
"""

tags_metadata = [
    {
        "name": "Autenticación",
        "description": "Endpoints para autenticación y gestión de sesiones. No requieren autenticación previa.",
    },
    {
        "name": "Clientes",
        "description": "Gestión de clientes y registro de visitas para tarjeta de fidelidad.",
    },
    {
        "name": "Usuarios",
        "description": "Gestión de usuarios/empleados del sistema. Requiere rol de administrador o superadministrador.",
    },
    {
        "name": "Productos",
        "description": "Gestión de productos del menú de la cafetería.",
    },
    {
        "name": "Inventario",
        "description": "Gestión de insumos, movimientos de inventario y alertas de stock bajo.",
    },
    {
        "name": "Ventas",
        "description": "Punto de venta - Registro de ventas y consulta de historial.",
    },
    {
        "name": "Comandas",
        "description": "Gestión de comandas para cocina. Los estados pueden ser: pendiente, en_preparacion, terminada, cancelada.",
    },
    {
        "name": "Recetas",
        "description": "Gestión de recetas que relacionan productos con insumos necesarios.",
    },
    {
        "name": "Pre-órdenes",
        "description": "Sistema de pedidos públicos desde la página web. Los clientes pueden crear pre-órdenes sin autenticación, que luego pasan por caja y cocina.",
    },
]

app = FastAPI(
    title="Sistema Control Inteligente API",
    description=description,
    version="1.0.0",
    terms_of_service="http://example.com/terms/",
    contact={
        "name": "Soporte API",
        "email": "soporte@cafeteria.com",
    },
    license_info={
        "name": "MIT",
    },
    openapi_tags=tags_metadata,
    docs_url="/docs",  # URL para Swagger UI
    redoc_url="/redoc",  # URL para ReDoc
    openapi_url="/openapi.json",  # URL para el schema OpenAPI
)

# Configuración CORS (para permitir peticiones desde el frontend)
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5174",
        "http://localhost:5173",
        "http://localhost:3000",
        "http://localhost:5175",
        "http://127.0.0.1:5174",
        "http://127.0.0.1:5173",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:5175",
    ],  # En producción, especificar solo los dominios permitidos
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS", "PATCH"],
    allow_headers=["*"],
    expose_headers=["*"],
)

# Manejo de errores de validación
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Maneja errores de validación y los devuelve en formato más legible"""
    errors = []
    for error in exc.errors():
        field = ".".join(str(loc) for loc in error["loc"])
        errors.append({
            "campo": field,
            "mensaje": error["msg"],
            "tipo": error["type"]
        })
    return JSONResponse(
        status_code=422,
        content={
            "error": "Error de validación",
            "detail": errors,
            "mensaje": f"Los siguientes campos tienen errores: {', '.join([e['campo'] for e in errors])}"
        }
    )

# Incluir todas las rutas
app.include_router(api_router)

@app.get("/", tags=["General"])
async def root():
    """
    Endpoint raíz de la API.
    
    Retorna información básica sobre la API y enlaces a la documentación.
    """
    return {
        "message": "Bienvenido a la API del Sistema de Control Inteligente",
        "version": "1.0.0",
        "documentation": {
            "swagger": "/docs",
            "redoc": "/redoc",
            "openapi": "/openapi.json"
        },
        "endpoints": {
            "autenticacion": "/api/login",
            "clientes": "/api/clientes",
            "usuarios": "/api/usuarios",
            "productos": "/api/productos",
            "inventario": "/api/inventario",
            "ventas": "/api/ventas",
            "comandas": "/api/comandas",
            "recetas": "/api/recetas",
            "preordenes": "/api/preordenes"
        }
    }

@app.get("/health", tags=["General"])
async def health_check():
    """
    Endpoint de salud de la API.
    
    Útil para verificar que el servidor está funcionando correctamente.
    """
    return {
        "status": "healthy",
        "service": "Sistema Control Inteligente API"
    }