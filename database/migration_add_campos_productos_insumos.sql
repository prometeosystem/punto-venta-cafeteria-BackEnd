-- Migración: Agregar campos tiempo_preparacion a productos y nombre_normalizado a insumos
-- Ejecutar este script si ya tienes una base de datos existente

-- 1. Agregar campo tiempo_preparacion a productos
ALTER TABLE productos 
ADD COLUMN IF NOT EXISTS tiempo_preparacion INT AFTER categoria;

-- Si tu versión de MySQL no soporta IF NOT EXISTS, usar esta versión:
-- ALTER TABLE productos 
-- ADD COLUMN tiempo_preparacion INT AFTER categoria;

-- 2. Agregar campo nombre_normalizado a insumos
ALTER TABLE insumos 
ADD COLUMN IF NOT EXISTS nombre_normalizado VARCHAR(255) AFTER nombre;

-- Si tu versión de MySQL no soporta IF NOT EXISTS, usar esta versión:
-- ALTER TABLE insumos 
-- ADD COLUMN nombre_normalizado VARCHAR(255) AFTER nombre;

-- 3. Crear índice único para nombre_normalizado
ALTER TABLE insumos 
ADD UNIQUE INDEX IF NOT EXISTS unique_nombre_normalizado (nombre_normalizado);

-- Si tu versión de MySQL no soporta IF NOT EXISTS, usar esta versión:
-- ALTER TABLE insumos 
-- ADD UNIQUE INDEX unique_nombre_normalizado (nombre_normalizado);

-- 4. NOTA IMPORTANTE: Después de ejecutar esta migración, necesitarás actualizar
-- manualmente los registros existentes de insumos con valores para nombre_normalizado.
-- Puedes usar un script Python o ejecutar esto por cada insumo:
-- 
-- UPDATE insumos SET nombre_normalizado = LOWER(REPLACE(REPLACE(REPLACE(REPLACE(REPLACE(
--   REPLACE(REPLACE(REPLACE(REPLACE(REPLACE(REPLACE(REPLACE(REPLACE(
--   nombre, 'á', 'a'), 'é', 'e'), 'í', 'i'), 'ó', 'o'), 'ú', 'u'),
--   'Á', 'A'), 'É', 'E'), 'Í', 'I'), 'Ó', 'O'), 'Ú', 'U'),
--   'ñ', 'n'), 'Ñ', 'N'))
-- WHERE nombre_normalizado IS NULL OR nombre_normalizado = '';

-- O mejor aún, usar el script Python de normalización que se encuentra en utils/normalize.py


