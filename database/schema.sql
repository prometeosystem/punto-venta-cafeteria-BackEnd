-- Base de datos para Sistema de Control Inteligente - Cafetería

-- Tabla de usuarios/empleados
CREATE TABLE IF NOT EXISTS usuarios (
    id_usuario INT AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL,
    apellido_paterno VARCHAR(100) NOT NULL,
    apellido_materno VARCHAR(100),
    correo VARCHAR(255) UNIQUE NOT NULL,
    user VARCHAR(100) UNIQUE,
    contrasena VARCHAR(255) NOT NULL,
    celular VARCHAR(20),
    rol ENUM('vendedor', 'cocina', 'administrador', 'superadministrador') NOT NULL,
    activo BOOLEAN DEFAULT TRUE,
    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    fecha_actualizacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

-- Tabla de clientes
CREATE TABLE IF NOT EXISTS clientes (
    id_cliente INT AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL,
    apellido_paterno VARCHAR(100) NOT NULL,
    apellido_materno VARCHAR(100),
    correo VARCHAR(255) UNIQUE NOT NULL,
    contrasena VARCHAR(255) NOT NULL,
    celular VARCHAR(20),
    rfc VARCHAR(20),
    direccion TEXT,
    puntos DECIMAL(10, 2) DEFAULT 0.00,
    loyabit_id VARCHAR(255) NULL,
    loyabit_sincronizado BOOLEAN DEFAULT FALSE,
    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    fecha_actualizacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

-- Tabla de productos
CREATE TABLE IF NOT EXISTS productos (
    id_producto INT AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(255) NOT NULL,
    descripcion TEXT,
    precio DECIMAL(10, 2) NOT NULL,
    categoria VARCHAR(100),
    tiempo_preparacion INT,
    activo BOOLEAN DEFAULT TRUE,
    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    fecha_actualizacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

-- Tabla de insumos (inventario)
CREATE TABLE IF NOT EXISTS insumos (
    id_insumo INT AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(255) NOT NULL,
    nombre_normalizado VARCHAR(255),
    descripcion TEXT,
    unidad_medida VARCHAR(50) NOT NULL, -- kg, litros, unidades, etc.
    cantidad_actual DECIMAL(10, 3) NOT NULL DEFAULT 0,
    cantidad_minima DECIMAL(10, 3) NOT NULL DEFAULT 0,
    precio_compra DECIMAL(10, 2),
    activo BOOLEAN DEFAULT TRUE,
    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    fecha_actualizacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

-- Tabla de movimientos de inventario
CREATE TABLE IF NOT EXISTS movimientos_inventario (
    id_movimiento INT AUTO_INCREMENT PRIMARY KEY,
    id_insumo INT NOT NULL,
    tipo_movimiento ENUM('entrada', 'salida') NOT NULL,
    cantidad DECIMAL(10, 3) NOT NULL,
    motivo VARCHAR(255) NOT NULL,
    observaciones TEXT,
    fecha_movimiento TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (id_insumo) REFERENCES insumos(id_insumo) ON DELETE CASCADE
);

-- Tabla de ventas
CREATE TABLE IF NOT EXISTS ventas (
    id_venta INT AUTO_INCREMENT PRIMARY KEY,
    id_cliente INT,
    id_usuario INT NOT NULL,
    total DECIMAL(10, 2) NOT NULL,
    metodo_pago ENUM('efectivo', 'tarjeta', 'transferencia') NOT NULL,
    fecha_venta TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (id_cliente) REFERENCES clientes(id_cliente) ON DELETE SET NULL,
    FOREIGN KEY (id_usuario) REFERENCES usuarios(id_usuario) ON DELETE RESTRICT
);

-- Tabla de detalles de venta
CREATE TABLE IF NOT EXISTS detalles_venta (
    id_detalle_venta INT AUTO_INCREMENT PRIMARY KEY,
    id_venta INT NOT NULL,
    id_producto INT NOT NULL,
    cantidad INT NOT NULL,
    precio_unitario DECIMAL(10, 2) NOT NULL,
    subtotal DECIMAL(10, 2) NOT NULL,
    FOREIGN KEY (id_venta) REFERENCES ventas(id_venta) ON DELETE CASCADE,
    FOREIGN KEY (id_producto) REFERENCES productos(id_producto) ON DELETE RESTRICT
);

-- Tabla de comandas
CREATE TABLE IF NOT EXISTS comandas (
    id_comanda INT AUTO_INCREMENT PRIMARY KEY,
    id_venta INT NOT NULL,
    estado ENUM('pendiente', 'en_preparacion', 'terminada', 'cancelada') DEFAULT 'pendiente',
    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    fecha_actualizacion TIMESTAMP,
    FOREIGN KEY (id_venta) REFERENCES ventas(id_venta) ON DELETE CASCADE
);

-- Tabla de detalles de comanda
CREATE TABLE IF NOT EXISTS detalles_comanda (
    id_detalle_comanda INT AUTO_INCREMENT PRIMARY KEY,
    id_comanda INT NOT NULL,
    id_producto INT NOT NULL,
    cantidad INT NOT NULL,
    observaciones TEXT,
    FOREIGN KEY (id_comanda) REFERENCES comandas(id_comanda) ON DELETE CASCADE,
    FOREIGN KEY (id_producto) REFERENCES productos(id_producto) ON DELETE RESTRICT
);

-- Tabla de recetas (relación producto-insumo)
CREATE TABLE IF NOT EXISTS recetas_insumos (
    id_receta INT AUTO_INCREMENT PRIMARY KEY,
    id_producto INT NOT NULL,
    id_insumo INT NOT NULL,
    cantidad_necesaria DECIMAL(10, 3) NOT NULL,
    FOREIGN KEY (id_producto) REFERENCES productos(id_producto) ON DELETE CASCADE,
    FOREIGN KEY (id_insumo) REFERENCES insumos(id_insumo) ON DELETE CASCADE,
    UNIQUE KEY unique_receta (id_producto, id_insumo)
);

-- Tabla de visitas de clientes (para tarjeta de fidelidad)
CREATE TABLE IF NOT EXISTS visitas_clientes (
    id_visita INT AUTO_INCREMENT PRIMARY KEY,
    id_cliente INT NOT NULL,
    id_venta INT NOT NULL,
    fecha_visita TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (id_cliente) REFERENCES clientes(id_cliente) ON DELETE CASCADE,
    FOREIGN KEY (id_venta) REFERENCES ventas(id_venta) ON DELETE CASCADE
);

-- Tabla de pre-órdenes (pedidos públicos desde la web)
CREATE TABLE IF NOT EXISTS preordenes (
    id_preorden INT AUTO_INCREMENT PRIMARY KEY,
    nombre_cliente VARCHAR(255),
    estado ENUM('preorden', 'en_caja', 'pagada', 'en_cocina', 'lista', 'entregada', 'cancelada') DEFAULT 'preorden',
    total DECIMAL(10, 2),
    id_venta INT,
    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    fecha_actualizacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (id_venta) REFERENCES ventas(id_venta) ON DELETE SET NULL
);

-- Tabla de detalles de pre-orden
CREATE TABLE IF NOT EXISTS detalles_preorden (
    id_detalle_preorden INT AUTO_INCREMENT PRIMARY KEY,
    id_preorden INT NOT NULL,
    id_producto INT NOT NULL,
    cantidad INT NOT NULL,
    observaciones TEXT,
    FOREIGN KEY (id_preorden) REFERENCES preordenes(id_preorden) ON DELETE CASCADE,
    FOREIGN KEY (id_producto) REFERENCES productos(id_producto) ON DELETE RESTRICT
);

-- Índices para mejorar rendimiento
-- Nota: IF NOT EXISTS no es soportado en todas las versiones de MySQL para índices
-- El sistema de inicialización manejará los errores de duplicados automáticamente
CREATE INDEX idx_ventas_fecha ON ventas(fecha_venta);
CREATE INDEX idx_ventas_cliente ON ventas(id_cliente);
CREATE INDEX idx_ventas_usuario ON ventas(id_usuario);
CREATE INDEX idx_comandas_estado ON comandas(estado);
CREATE INDEX idx_comandas_venta ON comandas(id_venta);
CREATE INDEX idx_visitas_cliente ON visitas_clientes(id_cliente);
CREATE INDEX idx_visitas_fecha ON visitas_clientes(fecha_visita);
CREATE INDEX idx_movimientos_insumo ON movimientos_inventario(id_insumo);
CREATE INDEX idx_movimientos_fecha ON movimientos_inventario(fecha_movimiento);
CREATE INDEX idx_preordenes_estado ON preordenes(estado);
CREATE INDEX idx_preordenes_fecha ON preordenes(fecha_creacion);
CREATE INDEX idx_loyabit_id ON clientes(loyabit_id);
CREATE UNIQUE INDEX unique_nombre_normalizado ON insumos(nombre_normalizado);

