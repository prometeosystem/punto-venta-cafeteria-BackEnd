# Cómo Activar la Integración con Loyabit

Esta guía te ayudará a activar la integración con Loyabit cuando estés listo.

## Pasos para Activar

### 1. Configurar Variables de Entorno

Crea un archivo `.env` en la raíz del proyecto con las credenciales de Loyabit:

```env
LOYABIT_API_KEY=tu_api_key_de_loyabit
LOYABIT_API_SECRET=tu_api_secret_de_loyabit
LOYABIT_BASE_URL=https://api.loyabit.com/v1
LOYABIT_MERCHANT_ID=tu_merchant_id
LOYABIT_AUTO_REGISTRO=false  # true para registro automático
```

### 2. Ejecutar Migración de Base de Datos

Si aún no lo has hecho, ejecuta la migración:

```sql
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

### 3. Ajustar el Cliente de API

Edita `utils/loyabit_client.py` y ajusta según la documentación oficial de Loyabit:

- URLs y endpoints (línea 18)
- Método de autenticación en `_get_headers()` (líneas 27-35)
- Estructura de payloads en los métodos
- Extracción de datos de respuestas

### 4. Descomentar las Rutas

Edita `routes/routes.py` y descomenta estas líneas:

```python
# Cambiar de:
# from controllers.loyabit_controller import router as loyabit_router

# A:
from controllers.loyabit_controller import router as loyabit_router

# Y descomentar:
api_router.include_router(loyabit_router, prefix="/api/loyabit", tags=["Loyabit"])
```

### 5. Activar Registro Automático (Opcional)

Si quieres que los clientes se registren automáticamente en Loyabit al crearlos:

Edita `services/cliente_service.py` y descomenta el bloque marcado con `# TODO: Descomentar cuando se configure la integración con Loyabit`

También descomenta la línea:
```python
import os
```

### 6. Instalar Dependencias

Asegúrate de tener instalado `requests`:

```bash
pip install -r requirements.txt
```

### 7. Reiniciar la Aplicación

Reinicia tu servidor FastAPI para que cargue las nuevas rutas y configuraciones.

### 8. Probar la Integración

Prueba los endpoints:

```bash
# Registrar un cliente en Loyabit
POST /api/loyabit/registrar_cliente/{id_cliente}

# Obtener información de un cliente
GET /api/loyabit/info_cliente/{id_cliente}
```

## Archivos que Contienen Código Comentado

1. **`routes/routes.py`**: Rutas de Loyabit comentadas
2. **`services/cliente_service.py`**: Registro automático comentado
3. **`utils/loyabit_client.py`**: Todo el código está activo, solo necesita ajustes según la API

## Notas Importantes

- El código de integración está completo y listo, solo está comentado para no activarlo accidentalmente
- Todos los archivos de integración están creados y funcionan
- Solo necesitas descomentar y ajustar según la documentación de Loyabit
- Consulta `README_LOYABIT.md` para más detalles sobre la integración


