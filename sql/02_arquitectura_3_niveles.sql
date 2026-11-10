-- ============================================================================
-- TPI 3 - Ampliación de Bases de Datos (Tema 6)
-- Arquitectura de Tres Niveles (ANSI/SPARC) e Independencia de Datos
-- Proyecto Mercadona (Sevilla) - Continuación sobre mercadona_bi
-- ============================================================================

-- Limpieza previa por si re-ejecutamos el script
DROP VIEW IF EXISTS vista_personal_tienda;
DROP VIEW IF EXISTS vista_direccion_mercadona;
DROP TABLE IF EXISTS reposiciones_stock;
DROP TABLE IF EXISTS productos_catalogo;
DROP TABLE IF EXISTS tiendas;

-- ============================================================================
-- 1. NIVEL CONCEPTUAL (Esquema lógico global, relaciones y restricciones)
-- ============================================================================

-- Tabla de las 5 tiendas de Mercadona en Sevilla
CREATE TABLE tiendas (
    id_tienda VARCHAR(30) PRIMARY KEY,
    nombre_tienda VARCHAR(100) NOT NULL,
    barrio VARCHAR(50) NOT NULL,
    encargado VARCHAR(80) NOT NULL
);

-- Catálogo de los 15 productos con dato confidencial (coste_proveedor)
CREATE TABLE productos_catalogo (
    id_producto VARCHAR(20) PRIMARY KEY,
    nombre_producto VARCHAR(100) NOT NULL,
    categoria VARCHAR(40) NOT NULL,
    precio_venta NUMERIC(6,2) NOT NULL CHECK (precio_venta > 0),
    coste_proveedor NUMERIC(6,2) NOT NULL CHECK (coste_proveedor > 0),
    stock_actual INT NOT NULL CHECK (stock_actual >= 0)
);

-- Tabla de reposiciones de stock en tienda vinculada a tiendas y productos
CREATE TABLE reposiciones_stock (
    id_reposicion SERIAL PRIMARY KEY,
    id_tienda VARCHAR(30) NOT NULL REFERENCES tiendas(id_tienda),
    id_producto VARCHAR(20) NOT NULL REFERENCES productos_catalogo(id_producto),
    unidades_reponer INT NOT NULL CHECK (unidades_reponer > 0),
    franja_horaria VARCHAR(10) NOT NULL,
    fecha_registro TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Inserción de las 5 tiendas de Sevilla (las mismas del CSV de Spark)
INSERT INTO tiendas (id_tienda, nombre_tienda, barrio, encargado) VALUES
('MERC_SEV_MACARENA',     'Mercadona Av. Doctor Fedriani', 'Macarena',     'Carlos Ruiz'),
('MERC_SEV_NERVION',      'Mercadona C/ Luis de Morales',  'Nervión',      'Laura Gómez'),
('MERC_SEV_TRIANA',       'Mercadona C/ San Jacinto',      'Triana',       'Miguel Ángel Torres'),
('MERC_SEV_LOS_REMEDIOS', 'Mercadona C/ Asunción',         'Los Remedios', 'Elena Morales'),
('MERC_SEV_BAMI',         'Mercadona C/ Bami',             'Bami',         'David Fernández');

-- Inserción de los 15 productos de Hacendado con su coste confidencial y stock
INSERT INTO productos_catalogo (id_producto, nombre_producto, categoria, precio_venta, coste_proveedor, stock_actual) VALUES
('PROD_01', 'Leche Entera Hacendado 1L',            'Lácteos',     0.95, 0.62, 450),
('PROD_02', 'Guacamole Hacendado 200g',             'Refrigerados',1.75, 1.05, 180),
('PROD_03', 'Pechuga de Pollo Fileteada 500g',      'Carnicería',  4.20, 2.95, 120),
('PROD_04', 'Aceite de Oliva Virgen Extra 1L',      'Despensa',    8.50, 6.40, 200),
('PROD_05', 'Cerveza Steinburg Pack 12',            'Bebidas',     3.60, 2.10, 320),
('PROD_06', 'Huevos Camperos Docena',               'Despensa',    2.65, 1.70, 210),
('PROD_07', 'Pan de Molde Blanco Hacendado',        'Panadería',   1.15, 0.65, 190),
('PROD_08', 'Atun Claro en Aceite de Oliva Pack 6', 'Conservas',   4.95, 3.40, 160),
('PROD_09', 'Yogur Griego Natural Pack 6',          'Lácteos',     1.60, 0.95, 240),
('PROD_10', 'Pizza Jamon y Queso Hacendado',        'Platos Prep.',2.90, 1.65, 150),
('PROD_11', 'Cafe Molido Natural Mezcla 250g',      'Despensa',    2.10, 1.30, 220),
('PROD_12', 'Salmorejo Fresco Hacendado 1L',        'Refrigerados',2.15, 1.25, 140),
('PROD_13', 'Papel Higienico Doble Rollo 12u',      'Hogar',       4.10, 2.60, 175),
('PROD_14', 'Queso Lonchas Havarti Hacendado',      'Charcutería', 2.25, 1.40, 165),
('PROD_15', 'Patatas Fritas Con Sal 150g',          'Aperitivos',  1.10, 0.58, 280);

-- Inserción de reposiciones iniciales en horas punta detectadas por Spark
INSERT INTO reposiciones_stock (id_tienda, id_producto, unidades_reponer, franja_horaria) VALUES
('MERC_SEV_NERVION',  'PROD_01', 120, '09:00'),
('MERC_SEV_MACARENA', 'PROD_05', 200, '12:00'),
('MERC_SEV_TRIANA',   'PROD_02', 80,  '15:00'),
('MERC_SEV_BAMI',     'PROD_10', 150, '18:00');


-- ============================================================================
-- 2. NIVEL INTERNO (Almacenamiento físico e índices B-Tree en disco)
-- ============================================================================

-- Índices físicos para acelerar búsquedas por tienda y por categoría en disco
CREATE INDEX idx_reposiciones_tienda ON reposiciones_stock USING btree (id_tienda);
CREATE INDEX idx_productos_categoria ON productos_catalogo USING btree (categoria);


-- ============================================================================
-- 3. NIVEL EXTERNO (Vistas personalizadas por rol y mínimo privilegio)
-- ============================================================================

-- Vista 1 (Personal de tienda / Reponedores):
-- Une los productos más vendidos por hora (del TPI 2 en Spark) con el catálogo,
-- pero OCULTA el coste_proveedor y el margen de beneficio.
CREATE VIEW vista_personal_tienda AS
SELECT
    pmv.franja_horaria,
    p.id_producto,
    p.nombre_producto,
    p.categoria,
    p.precio_venta,
    pmv.unidades_totales AS unidades_vendidas_tramo,
    p.stock_actual
FROM producto_mas_vendido_tramo pmv
JOIN productos_catalogo p ON pmv.id_producto = p.id_producto
WHERE pmv.tipo_ventana = '1_HORA'
ORDER BY pmv.franja_horaria;

-- Vista 2 (Dirección Financiera / Jefes de Zona):
-- Muestra el coste_proveedor, el margen unitario y el beneficio neto en euros por hora.
CREATE VIEW vista_direccion_mercadona AS
SELECT
    pmv.franja_horaria,
    p.id_producto,
    p.nombre_producto,
    pmv.unidades_totales,
    p.precio_venta,
    p.coste_proveedor,
    (p.precio_venta - p.coste_proveedor) AS margen_unitario_eur,
    ROUND((pmv.unidades_totales * (p.precio_venta - p.coste_proveedor))::numeric, 2) AS beneficio_neto_tramo_eur
FROM producto_mas_vendido_tramo pmv
JOIN productos_catalogo p ON pmv.id_producto = p.id_producto
WHERE pmv.tipo_ventana = '1_HORA'
ORDER BY pmv.franja_horaria;

-- Creación de un rol con privilegios mínimos para los terminales de tienda
DO $$
BEGIN
    IF NOT EXISTS (SELECT FROM pg_catalog.pg_roles WHERE rolname = 'empleado_tienda') THEN
        CREATE ROLE empleado_tienda LOGIN PASSWORD 'tienda_pass';
    END IF;
END
$$;

REVOKE ALL ON productos_catalogo FROM empleado_tienda;
GRANT SELECT ON vista_personal_tienda TO empleado_tienda;


-- ============================================================================
-- 4. DEMOSTRACIÓN DE INDEPENDENCIA DE DATOS (Física y Lógica)
-- ============================================================================

-- A) INDEPENDENCIA FÍSICA:
-- Añadimos un nuevo índice en el nivel interno para filtrar por franja_horaria.
-- Ni el nivel conceptual ni las vistas externas sufren ningún cambio.
CREATE INDEX idx_reposiciones_franja ON reposiciones_stock USING btree (franja_horaria);

-- B) INDEPENDENCIA LÓGICA:
-- Modificamos el nivel conceptual añadiendo una nueva columna 'pasillo_ubicacion'
-- a la tabla 'productos_catalogo'. Las aplicaciones que consultan 'vista_personal_tienda'
-- o 'vista_direccion_mercadona' siguen funcionando sin romper su código.
ALTER TABLE productos_catalogo
ADD COLUMN pasillo_ubicacion VARCHAR(30) DEFAULT 'Pasillo Central';
