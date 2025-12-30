# Sistema de Control Inteligente - API para Cafetería

API REST desarrollada con FastAPI para la gestión integral de una cafetería, incluyendo punto de venta, comandas, inventario, clientes y sistema de roles.

## Características Principales

- **Sistema de Autenticación y Roles**: Vendedor, Cocina, Administrador, Superadministrador
- **Punto de Venta**: Registro de ventas con múltiples métodos de pago
- **Sistema de Comandas**: Gestión de órdenes con estados (pendiente, en preparación, terminada)
- **Inventario Automático**: Resta automática de insumos cuando una comanda se marca como terminada
- **Gestión de Clientes**: Registro de visitas para tarjeta de fidelidad (preparado para integración con Loyabit)
- **Gestión de Productos e Insumos**: Control completo de productos y recetas
- **Reportes**: Base preparada para análisis de datos

## Estructura del Proyecto

```
SistemaControlInteligente/
├── controllers/          # Controladores de endpoints
├── services/            # Lógica de negocio
├── repository/          # Acceso a base de datos
├── schemas/             # Modelos Pydantic para validación
├── database/            # Configuración y esquema de BD
├── routes/              # Configuración de rutas
├── utils/               # Utilidades (autenticación, etc.)
└── main.py             # Punto de entrada de la aplicación
```

## Instalación

1. **Clonar el repositorio** (si aplica)

2. **Instalar dependencias**:
```bash
pip install -r requirements.txt
```

3. **Configurar la base de datos**:
   - Crear la base de datos MySQL: `sistema_control_inteligente`
   - Ejecutar el script SQL: `database/schema.sql`
   - Actualizar las credenciales en `database/conexion.py`

4. **Configurar variables de seguridad**:
   - Editar `utils/auth.py` y cambiar `SECRET_KEY` por una clave segura

## Uso

### Iniciar el servidor:

```bash
uvicorn main:app --reload
```

La API estará disponible en: `http://localhost:8000`

### Documentación interactiva:

- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## Endpoints Principales

### Autenticación
- `POST /api/login` - Iniciar sesión
- `GET /api/me` - Obtener información del usuario actual

### Clientes
- `POST /api/clientes/crear_cliente` - Crear cliente
- `GET /api/clientes/ver_clientes` - Listar clientes
- `GET /api/clientes/ver_cliente/{id}` - Ver cliente específico
- `POST /api/clientes/registrar_visita` - Registrar visita (para fidelidad)
- `GET /api/clientes/visitas_cliente/{id}` - Ver visitas de un cliente

### Usuarios/Empleados
- `POST /api/usuarios/crear_usuario` - Crear usuario (solo admin)
- `GET /api/usuarios/ver_usuarios` - Listar usuarios (solo admin)

### Productos
- `POST /api/productos/crear_producto` - Crear producto
- `GET /api/productos/ver_productos` - Listar productos

### Inventario
- `POST /api/inventario/crear_insumo` - Crear insumo
- `GET /api/inventario/ver_insumos` - Listar insumos
- `GET /api/inventario/insumos_bajo_stock` - Ver insumos con stock bajo

### Ventas
- `POST /api/ventas/crear_venta` - Crear venta (punto de venta)
- `GET /api/ventas/ver_ventas` - Listar ventas
- `GET /api/ventas/ver_venta/{id}` - Ver venta específica

### Comandas
- `POST /api/comandas/crear_comanda` - Crear comanda
- `GET /api/comandas/ver_comandas` - Listar comandas
- `PUT /api/comandas/actualizar_estado_comanda/{id}` - Actualizar estado (cocina)

### Recetas
- `POST /api/recetas/crear_receta` - Crear receta (producto-insumo)
- `GET /api/recetas/ver_recetas_producto/{id}` - Ver recetas de un producto

## Flujo de Trabajo

1. **Venta**: El vendedor crea una venta con productos
2. **Comanda**: Se crea automáticamente una comanda asociada a la venta
3. **Cocina**: La cocina ve las comandas pendientes y actualiza el estado
4. **Inventario**: Cuando la comanda se marca como "terminada", se restan automáticamente los insumos según las recetas
5. **Cliente**: Si hay cliente asociado, se registra la visita para fidelidad

## Roles y Permisos

- **Vendedor**: Puede crear ventas y comandas
- **Cocina**: Puede ver y actualizar estados de comandas
- **Administrador**: Gestión completa excepto usuarios
- **Superadministrador**: Acceso total al sistema

## Próximas Mejoras

- Integración con Loyabit para tarjeta de fidelidad
- Módulo de reportes con análisis de datos
- Dashboard con métricas en tiempo real
- Notificaciones push para comandas
- Integración con sistemas de pago

## Notas

- La contraseña de los clientes debe ser hasheada antes de guardarse (pendiente de implementar)
- El sistema está preparado para análisis de datos en el módulo de reportes
- La integración con Loyabit se realizará en una fase posterior

