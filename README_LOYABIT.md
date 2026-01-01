# Integración con Loyabit

Este sistema incluye integración con Loyabit para gestión de programas de fidelización de clientes.

## Configuración

### 1. Variables de Entorno

Crea un archivo `.env` en la raíz del proyecto con las siguientes variables:

```env
LOYABIT_API_KEY=tu_api_key_de_loyabit
LOYABIT_API_SECRET=tu_api_secret_de_loyabit
LOYABIT_BASE_URL=https://api.loyabit.com/v1
LOYABIT_MERCHANT_ID=tu_merchant_id
LOYABIT_AUTO_REGISTRO=false  # true para registro automático de clientes
```

### 2. Obtener Credenciales

1. Accede a tu cuenta de Loyabit
2. Ve a la sección de desarrolladores/API
3. Genera o copia tus credenciales (API Key, API Secret, Merchant ID)
4. Configura las variables de entorno

### 3. Migración de Base de Datos

Si ya tienes una base de datos existente, ejecuta el script de migración:

```sql
-- Ejecutar desde MySQL
source database/migration_add_loyabit_fields.sql;
```

O manualmente:

```sql
ALTER TABLE clientes 
ADD COLUMN loyabit_id VARCHAR(255) NULL AFTER puntos,
ADD COLUMN loyabit_sincronizado BOOLEAN DEFAULT FALSE AFTER loyabit_id;

ALTER TABLE clientes 
ADD INDEX idx_loyabit_id (loyabit_id);
```

## Ajustar el Cliente de API

**IMPORTANTE**: El cliente de API (`utils/loyabit_client.py`) está configurado de forma genérica. Debes ajustarlo según la documentación oficial de la API de Loyabit:

1. **URLs y Endpoints**: Ajusta `base_url` y los endpoints según la documentación
2. **Autenticación**: Ajusta `_get_headers()` según el método de autenticación que use Loyabit
3. **Estructura de Datos**: Ajusta los payloads en los métodos según la estructura que espera la API
4. **Respuestas**: Ajusta cómo se extraen los datos de las respuestas (ej: `respuesta.get("id")`)

## Uso de los Endpoints

### 1. Registrar Cliente en Loyabit

Registra un cliente existente en Loyabit:

```http
POST /api/loyabit/registrar_cliente/{id_cliente}
```

**Permisos**: Administrador o Superadministrador

### 2. Obtener Información de Cliente

Obtiene información de un cliente desde Loyabit (incluye puntos):

```http
GET /api/loyabit/info_cliente/{id_cliente}
```

**Permisos**: Cualquier usuario autenticado

### 3. Sincronizar Cliente

Sincroniza un cliente con Loyabit (registra si no existe, actualiza si existe):

```http
POST /api/loyabit/sincronizar_cliente
Content-Type: application/json

{
  "id_cliente": 1,
  "forzar_sincronizacion": false
}
```

**Permisos**: Administrador o Superadministrador

### 4. Agregar Puntos

Agrega puntos a un cliente después de una compra:

```http
POST /api/loyabit/agregar_puntos
Content-Type: application/json

{
  "id_cliente": 1,
  "puntos": 50.0,
  "motivo": "Compra realizada"
}
```

**Permisos**: Vendedor, Administrador o Superadministrador

### 5. Canjear Puntos

Canjea puntos de un cliente:

```http
POST /api/loyabit/canjear_puntos
Content-Type: application/json

{
  "id_cliente": 1,
  "puntos": 100.0,
  "motivo": "Canje de puntos"
}
```

**Permisos**: Vendedor, Administrador o Superadministrador

## Registro Automático

Si configuras `LOYABIT_AUTO_REGISTRO=true`, los clientes se registrarán automáticamente en Loyabit cuando se creen en el sistema.

## Integración con Ventas

Para integrar automáticamente con las ventas, puedes modificar el servicio de ventas para que:

1. Después de crear una venta, agregue puntos al cliente si está registrado en Loyabit
2. Use los puntos del cliente para aplicar descuentos

Ejemplo en el código de ventas:

```python
# Después de crear una venta
if venta.id_cliente:
    from services.loyabit_service import agregar_puntos_loyabit
    puntos_ganados = calcular_puntos(venta.total)  # Tu lógica de cálculo
    agregar_puntos_loyabit(venta.id_cliente, puntos_ganados, "Compra realizada")
```

## Troubleshooting

### Error: "Servicio de Loyabit no configurado"

- Verifica que las variables de entorno estén configuradas
- Reinicia la aplicación después de cambiar las variables de entorno

### Error: "Error en API de Loyabit"

- Verifica que las credenciales sean correctas
- Verifica que la URL base sea correcta
- Revisa los logs para más detalles del error
- Consulta la documentación oficial de la API de Loyabit

### Cliente no se sincroniza

- Verifica que el cliente exista en la base de datos local
- Revisa que las credenciales de API sean válidas
- Verifica los logs del servidor para errores específicos

## Próximos Pasos

1. Obtén la documentación oficial de la API de Loyabit
2. Ajusta `utils/loyabit_client.py` según la documentación
3. Configura las variables de entorno
4. Ejecuta las migraciones de base de datos
5. Prueba la integración con un cliente de prueba
6. Configura la integración automática con ventas si lo deseas


