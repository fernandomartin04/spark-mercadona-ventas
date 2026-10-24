-- Inicialización de la base de datos empresarial de Mercadona (Data Mart BI)
-- Ampliación de Bases de Datos - TPI 2

CREATE TABLE IF NOT EXISTS control_cargas (
    id SERIAL PRIMARY KEY,
    proceso VARCHAR(100) NOT NULL,
    filas_procesadas INT,
    fecha_ejecucion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    estado VARCHAR(20) DEFAULT 'EXITO'
);
