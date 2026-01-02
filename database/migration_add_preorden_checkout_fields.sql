-- Migración: Agregar campos del modal de checkout a la tabla preordenes
-- Fecha: 2024
-- Descripción: Agrega campos para tipo de servicio, comentarios, tipo de leche y extra por leche deslactosada

ALTER TABLE preordenes 
ADD COLUMN tipo_servicio VARCHAR(20) NULL COMMENT 'comer-aqui o para-llevar',
ADD COLUMN comentarios TEXT NULL COMMENT 'Comentarios generales del pedido',
ADD COLUMN tipo_leche VARCHAR(20) NULL COMMENT 'entera o deslactosada',
ADD COLUMN extra_leche DECIMAL(10,2) DEFAULT 0 COMMENT 'Monto extra por leche deslactosada';

