-- Migración para agregar campo de imagen a productos
-- Las imágenes se almacenan como BLOB en la base de datos

ALTER TABLE productos 
ADD COLUMN imagen LONGBLOB NULL AFTER categoria,
ADD COLUMN tipo_imagen VARCHAR(50) NULL AFTER imagen;

