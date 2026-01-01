-- Migración: Agregar campos de integración con Loyabit a la tabla clientes
-- Ejecutar este script si ya tienes una base de datos existente

-- Agregar campo loyabit_id (ID del cliente en Loyabit)
ALTER TABLE clientes 
ADD COLUMN IF NOT EXISTS loyabit_id VARCHAR(255) NULL AFTER puntos;

-- Si tu versión de MySQL no soporta IF NOT EXISTS, usar esta versión:
-- ALTER TABLE clientes 
-- ADD COLUMN loyabit_id VARCHAR(255) NULL AFTER puntos;

-- Agregar campo loyabit_sincronizado (indica si está sincronizado con Loyabit)
ALTER TABLE clientes 
ADD COLUMN IF NOT EXISTS loyabit_sincronizado BOOLEAN DEFAULT FALSE AFTER loyabit_id;

-- Si tu versión de MySQL no soporta IF NOT EXISTS, usar esta versión:
-- ALTER TABLE clientes 
-- ADD COLUMN loyabit_sincronizado BOOLEAN DEFAULT FALSE AFTER loyabit_id;

-- Crear índice para búsquedas por loyabit_id
ALTER TABLE clientes 
ADD INDEX IF NOT EXISTS idx_loyabit_id (loyabit_id);

-- Si tu versión de MySQL no soporta IF NOT EXISTS, usar esta versión:
-- ALTER TABLE clientes 
-- ADD INDEX idx_loyabit_id (loyabit_id);


