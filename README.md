# 🛒 Análisis de Ventas y Stock en Mercadona (Spark SQL + PostgreSQL + Docker)

Proyecto práctico de **Big Data e Integración Empresarial** desarrollado para la asignatura **Ampliación de Bases de Datos** (Grado en Ingeniería del Software, Universidad Loyola Andalucía).

El objetivo es procesar un archivo masivo de **50.000 ventas de caja** (`ventas_mercadona.csv`) mediante **Apache Spark SQL** para obtener de forma rápida:
1. **La recaudación y la venta media en euros (€)** por tramos de **1 hora** y de **30 minutos**.
2. **El producto más vendido** (en unidades y euros) en cada tramo de **1 hora** y de **30 minutos**.
3. **La integración empresarial (JDBC)** guardando los resultados ya resumidos en **PostgreSQL** (`mercadona_bi`) y mostrándolos en un panel web sencillo (`panel_mercadona.html`).

---

## 🚀 Tecnologías Utilizadas

* **Procesamiento Big Data (Apartado 5.4):** Apache Spark 3.5.3 y PySpark (`Spark SQL`).
* **Integración Empresarial (Apartado 5.5):** PostgreSQL 16 (`postgres:16-alpine`) conectado mediante el driver oficial JDBC (`postgresql-42.7.4.jar`).
* **Contenerización:** Docker y Docker Compose.
* **Interfaz de Consulta:** HTML5, CSS3 y JavaScript (`panel_mercadona.html`).

---

## 📁 Estructura del Repositorio

| Archivo / Carpeta | Descripción |
| :--- | :--- |
| [`docker-compose.yml`](docker-compose.yml) | Levanta los contenedores `mercadona_spark` y `mercadona_postgres` conectados en red. |
| [`scripts/01_generar_datos.py`](scripts/01_generar_datos.py) | Genera el CSV con 50.000 ventas de productos de Mercadona entre las 09:00 y las 21:00. |
| [`scripts/02_procesar_spark_sql.py`](scripts/02_procesar_spark_sql.py) | Script PySpark que ejecuta las consultas de Spark SQL y guarda las tablas en PostgreSQL por JDBC. |
| [`scripts/03_generar_panel_web.py`](scripts/03_generar_panel_web.py) | Consulta las tablas de PostgreSQL y actualiza el panel web interactivo. |
| [`panel_mercadona.html`](panel_mercadona.html) | Página web sencilla para consultar la venta media y el producto más vendido por 1h o 30 min. |
| [`data/ventas_mercadona.csv`](data/ventas_mercadona.csv) | Dataset generado con las 50.000 líneas de venta (~4,4 MB). |
| [`TPI_2_Memoria.tex`](TPI_2_Memoria.tex) | Código fuente en LaTeX de la memoria del TPI 2. |
| `imgs/` | Capturas de pantalla reales de la ejecución y del panel web. |

---

## 🛠️ Puesta en Marcha Paso a Paso

### 1. Levantar los contenedores con Docker
```bash
docker compose up -d
```

### 2. Generar el CSV de 50.000 ventas (opcional, ya incluido en `data/`)
```bash
python3 scripts/01_generar_datos.py
```

### 3. Procesar con Spark SQL y volcar a PostgreSQL (JDBC)
```bash
docker exec mercadona_spark /opt/spark/bin/spark-submit \
  --jars /app/jars/postgresql-42.7.4.jar \
  /app/scripts/02_procesar_spark_sql.py
```

### 4. Comprobar las tablas guardadas en PostgreSQL
```bash
docker exec mercadona_postgres psql -U postgres -d mercadona_bi \
  -c "SELECT * FROM resumen_ventas_tramo WHERE tipo_ventana = '1_HORA';" \
  -c "SELECT * FROM producto_mas_vendido_tramo WHERE tipo_ventana = '30_MIN' LIMIT 10;"
```

### 5. Actualizar y abrir el panel web
```bash
python3 scripts/03_generar_panel_web.py
xdg-open panel_mercadona.html
```
