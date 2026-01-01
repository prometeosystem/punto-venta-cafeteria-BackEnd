-- Migración: Agregar campo 'user' a la tabla usuarios
-- Ejecutar este script si ya tienes una base de datos existente

-- Agregar columna user (si no existe)
ALTER TABLE usuarios 
ADD COLUMN IF NOT EXISTS user VARCHAR(100) UNIQUE AFTER correo;

-- Si tu versión de MySQL no soporta IF NOT EXISTS, usar esta versión:
-- ALTER TABLE usuarios 
-- ADD COLUMN user VARCHAR(100) UNIQUE AFTER correo;

-- NOTA: Después de ejecutar esta migración, necesitarás actualizar manualmente
-- los registros existentes con valores para el campo 'user', por ejemplo:
-- UPDATE usuarios SET user = CONCAT('user', id_usuario) WHERE user IS NULL;


