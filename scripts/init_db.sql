-- scripts/init_db.sql
-- Script de inicialización de la base de datos PostgreSQL.
-- Ejecutar con: psql -U tu_usuario -d mi_base_de_datos -f scripts/init_db.sql

-- ── Tabla de clientes ──────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS clientes (
    id              SERIAL PRIMARY KEY,
    nombre          VARCHAR(200) NOT NULL,
    ruc             VARCHAR(13)  UNIQUE,
    email           VARCHAR(150),
    telefono        VARCHAR(20),
    direccion       TEXT,
    fecha_registro  TIMESTAMP DEFAULT NOW()
);

-- ── Tabla de facturas ──────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS facturas (
    id                    SERIAL PRIMARY KEY,
    numero_factura        VARCHAR(20)    NOT NULL,
    fecha_emision         DATE           NOT NULL,
    ruc_emisor            VARCHAR(13)    NOT NULL,
    razon_social_emisor   VARCHAR(200)   NOT NULL,
    ruc_receptor          VARCHAR(13)    NOT NULL,
    razon_social_receptor VARCHAR(200)   NOT NULL,
    subtotal              NUMERIC(12, 2) NOT NULL DEFAULT 0,
    iva                   NUMERIC(12, 2) NOT NULL DEFAULT 0,
    total                 NUMERIC(12, 2) NOT NULL DEFAULT 0,
    estado                VARCHAR(20)    NOT NULL DEFAULT 'PENDIENTE',
    CONSTRAINT uq_factura UNIQUE (ruc_emisor, numero_factura)
);

-- ── Datos de prueba ────────────────────────────────────────────────────────
INSERT INTO clientes (nombre, ruc, email, telefono, direccion)
VALUES
    ('Empresa Demo S.A.', '1790012345001', 'demo@empresa.com', '02-2345678', 'Av. Amazonas 123, Quito'),
    ('Juan Pérez', '1712345678001', 'juan@email.com', '099-1234567', 'Calle Sucre 456, Guayaquil')
ON CONFLICT DO NOTHING;

INSERT INTO facturas (numero_factura, fecha_emision, ruc_emisor, razon_social_emisor,
                      ruc_receptor, razon_social_receptor, subtotal, iva, total, estado)
VALUES
    ('001-001-000000001', '2024-01-15', '1790012345001', 'Empresa Demo S.A.',
     '1712345678001', 'Juan Pérez', 1000.00, 150.00, 1150.00, 'AUTORIZADA'),
    ('001-001-000000002', '2024-02-20', '1790012345001', 'Empresa Demo S.A.',
     '0999999999001', 'Cliente Externo Cía. Ltda.', 500.00, 75.00, 575.00, 'AUTORIZADA')
ON CONFLICT DO NOTHING;

SELECT 'Base de datos inicializada correctamente.' AS resultado;
