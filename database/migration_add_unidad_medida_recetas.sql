-- Migración para agregar campo unidad_medida a recetas_insumos
-- La unidad de medida va en la receta (cuánto se necesita para el producto), no en el insumo

ALTER TABLE recetas_insumos 
ADD COLUMN unidad_medida VARCHAR(50) NOT NULL DEFAULT 'gramos' AFTER cantidad_necesaria;

