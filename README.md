# 🛒 Análisis de Ventas y Stock en Mercadona (Spark SQL + PostgreSQL + Docker)

Proyecto práctico de **Big Data, Integración Empresarial y Arquitectura de Acceso a Datos** desarrollado para la asignatura **Ampliación de Bases de Datos** (Grado en Ingeniería del Software, Universidad Loyola Andalucía).

El proyecto está organizado en dos fases complementarias sobre la misma base de datos PostgreSQL (`mercadona_bi`):
* **Fase 1 (TPI 2 — Tema 5):** Procesamiento de un archivo masivo de **50.000 ventas de caja** (`ventas_mercadona.csv`) mediante **Apache Spark SQL** para obtener la venta media y el producto más vendido en tramos de **1 hora** y **30 minutos**, integrando los resultados en PostgreSQL (`panel_mercadona.html`).
* **Fase 2 (TPI 3 — Tema 6):** Implementación sobre `mercadona_bi` de la **Arquitectura de Tres Niveles (Interno, Conceptual y Externo)**, pruebas de **Independencia Física y Lógica**, acceso mediante **ODBC (`pyodbc`)**, **JDBC**, mapeo objeto-relacional con **ORM Hibernate** y **Buenas Prácticas** (`panel_arquitectura_tpi3.html`).

---

## 🚀 Tecnologías Utilizadas

* **Procesamiento Big Data (TPI 2):** Apache Spark 3.5.3 y PySpark (`Spark SQL`).
* **Base de Datos y Arquitectura de 3 Niveles (TPI 2 y TPI 3):** PostgreSQL 16 (`postgres:16-alpine`), vistas por rol (`VIEW`), control de privilegios (`GRANT`/`REVOKE`) e índices B-Tree.
* **Interfaces de Acceso y ORM (TPI 3):**
  * **ODBC:** Driver `PostgreSQL Unicode` (`psqlodbc`) con `pyodbc` en Python.
  * **JDBC:** Driver oficial `postgresql-42.7.4.jar` con `PreparedStatement` y transacciones ACID en Java.
  * **ORM:** **Hibernate Core 5.6** mapeando la entidad `ProductoCatalogo` en Java.
* **Contenerización e Interfaces:** Docker, Docker Compose y paneles web HTML5/CSS3 (`panel_mercadona.html` y `panel_arquitectura_tpi3.html`).

---

## 📁 Estructura del Repositorio

| Archivo / Carpeta | Descripción |
| :--- | :--- |
| [`docker-compose.yml`](docker-compose.yml) | Levanta los contenedores `mercadona_spark` y `mercadona_postgres` conectados en red. |
| [`scripts/01_generar_datos.py`](scripts/01_generar_datos.py) | **(TPI 2)** Genera el CSV con 50.000 ventas de productos de Mercadona entre las 09:00 y las 21:00. |
| [`scripts/02_procesar_spark_sql.py`](scripts/02_procesar_spark_sql.py) | **(TPI 2)** Script PySpark que ejecuta las consultas de Spark SQL y guarda las tablas en PostgreSQL por JDBC. |
| [`scripts/03_generar_panel_web.py`](scripts/03_generar_panel_web.py) | **(TPI 2)** Consulta las tablas de PostgreSQL y actualiza `panel_mercadona.html`. |
| [`sql/02_arquitectura_3_niveles.sql`](sql/02_arquitectura_3_niveles.sql) | **(TPI 3)** Crea el nivel conceptual (`tiendas`, `productos_catalogo`, `reposiciones_stock`), nivel interno (índices B-Tree), nivel externo (`vista_personal_tienda` y `vista_direccion_mercadona`), rol restringido e independencia de datos. |
| [`scripts/04_acceso_odbc.py`](scripts/04_acceso_odbc.py) | **(TPI 3)** Conexión mediante interfaz **ODBC** con el rol `empleado_tienda` verificando el bloqueo del coste de proveedor. |
| [`java_app/`](java_app) | **(TPI 3)** Aplicación Java con Maven (`AppMercadona.java` y entidad `ProductoCatalogo.java`) que demuestra el acceso con **JDBC** (transacción ACID + `PreparedStatement`) y **ORM Hibernate**. |
| [`scripts/05_generar_panel_tpi3.py`](scripts/05_generar_panel_tpi3.py) | **(TPI 3)** Genera el visor web comparativo `panel_arquitectura_tpi3.html`. |
| [`panel_mercadona.html`](panel_mercadona.html) | Visor web del TPI 2 (ventas por tramos de 1h y 30m). |
| [`panel_arquitectura_tpi3.html`](panel_arquitectura_tpi3.html) | Visor web del TPI 3 (vistas del nivel externo y actualizaciones de JDBC/Hibernate). |

---

## 🛠️ Puesta en Marcha Paso a Paso (TPI 2: Spark SQL)

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

### 4. Comprobar las tablas guardadas en PostgreSQL y abrir el panel
```bash
python3 scripts/03_generar_panel_web.py
xdg-open panel_mercadona.html
```

---

## 🔐 Puesta en Marcha Paso a Paso (TPI 3: Arquitectura de 3 Niveles, ODBC, JDBC e Hibernate)

### 1. Crear los 3 niveles (Interno, Conceptual y Externo) e Independencia de Datos
```bash
docker exec -i mercadona_postgres psql -U postgres -d mercadona_bi < sql/02_arquitectura_3_niveles.sql
```

### 2. Ejecutar el acceso mediante interfaz ODBC (`empleado_tienda`)
```bash
docker exec mercadona_spark python3 /app/scripts/04_acceso_odbc.py
```

### 3. Ejecutar la aplicación Java (JDBC + Transacción ACID + ORM Hibernate)
```bash
docker exec -w /app/java_app mercadona_spark bash -c \
  "JAVA_HOME=/usr/lib/jvm/java-11-openjdk-amd64 mvn -q compile exec:java -Dexec.mainClass=mercadona.AppMercadona"
```

### 4. Generar y abrir el visor web de las vistas del Nivel Externo
```bash
python3 scripts/05_generar_panel_tpi3.py
xdg-open panel_arquitectura_tpi3.html
```
