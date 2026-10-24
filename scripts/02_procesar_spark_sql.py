from pyspark.sql import SparkSession

# 1. Inicializar la sesión de Spark con el conector JDBC de PostgreSQL
spark = SparkSession.builder \
    .appName("Mercadona_SparkSQL_Analisis") \
    .config("spark.jars", "/app/jars/postgresql-42.7.4.jar") \
    .getOrCreate()

spark.sparkContext.setLogLevel("WARN")

print("==========================================================")
print("1. CARGANDO CSV MASIVO DE VENTAS DE MERCADONA (50.000 FILAS)")
print("==========================================================")

df_ventas = spark.read.csv(
    "/app/data/ventas_mercadona.csv",
    header=True,
    inferSchema=True
)

print(f"Total de líneas de venta leídas: {df_ventas.count()}")
df_ventas.createOrReplaceTempView("ventas_brutas")

# -------------------------------------------------------------------------
# PASO 1: Clasificar cada venta en su tramo de 1 hora y de 30 minutos
# Sintaxis SQL estándar y muy fácil de leer: DATE_FORMAT y CASE WHEN
# -------------------------------------------------------------------------
df_con_tramos = spark.sql("""
    SELECT
        id_venta,
        fecha_hora,
        id_tienda,
        id_producto,
        nombre_producto,
        cantidad,
        importe_total,
        DATE_FORMAT(fecha_hora, 'HH:00') AS tramo_1h,
        CASE
            WHEN MINUTE(fecha_hora) < 30 THEN DATE_FORMAT(fecha_hora, 'HH:00')
            ELSE DATE_FORMAT(fecha_hora, 'HH:30')
        END AS tramo_30m
    FROM ventas_brutas
""")
df_con_tramos.createOrReplaceTempView("ventas_con_tramos")

# -------------------------------------------------------------------------
# PASO 2: Calcular recaudación por tramo (1h y 30m) y la VENTA MEDIA (€)
# -------------------------------------------------------------------------
print("\n==========================================================")
print("2. CALCULANDO VENTA MEDIA Y RECAUDACIÓN POR TRAMOS (SPARK SQL)")
print("==========================================================")

df_tramos_unidos = spark.sql("""
    SELECT
        '1_HORA' AS tipo_ventana,
        tramo_1h AS franja_horaria,
        COUNT(*) AS numero_ventas,
        ROUND(SUM(importe_total), 2) AS recaudacion_euros
    FROM ventas_con_tramos
    GROUP BY tramo_1h

    UNION ALL

    SELECT
        '30_MIN' AS tipo_ventana,
        tramo_30m AS franja_horaria,
        COUNT(*) AS numero_ventas,
        ROUND(SUM(importe_total), 2) AS recaudacion_euros
    FROM ventas_con_tramos
    GROUP BY tramo_30m
""")
df_tramos_unidos.createOrReplaceTempView("tramos_agrupados")

# Añadimos la media global de cada tipo de ventana con AVG()
df_resumen_ventas = spark.sql("""
    SELECT
        tipo_ventana,
        franja_horaria,
        numero_ventas,
        recaudacion_euros,
        ROUND(AVG(recaudacion_euros) OVER (PARTITION BY tipo_ventana), 2) AS media_global_euros
    FROM tramos_agrupados
    ORDER BY tipo_ventana, franja_horaria
""")

print(">>> Muestra de recaudación y media por tramos de 1 HORA:")
df_resumen_ventas.filter("tipo_ventana = '1_HORA'").show(12, truncate=False)

# -------------------------------------------------------------------------
# PASO 3: Calcular el PRODUCTO MÁS VENDIDO en cada tramo de 1h y 30m
# -------------------------------------------------------------------------
print("\n==========================================================")
print("3. CALCULANDO EL PRODUCTO MÁS VENDIDO POR TRAMO (SPARK SQL)")
print("==========================================================")

df_productos_agrupados = spark.sql("""
    SELECT
        '1_HORA' AS tipo_ventana,
        tramo_1h AS franja_horaria,
        id_producto,
        nombre_producto,
        SUM(cantidad) AS unidades_totales,
        ROUND(SUM(importe_total), 2) AS euros_producto
    FROM ventas_con_tramos
    GROUP BY tramo_1h, id_producto, nombre_producto

    UNION ALL

    SELECT
        '30_MIN' AS tipo_ventana,
        tramo_30m AS franja_horaria,
        id_producto,
        nombre_producto,
        SUM(cantidad) AS unidades_totales,
        ROUND(SUM(importe_total), 2) AS euros_producto
    FROM ventas_con_tramos
    GROUP BY tramo_30m, id_producto, nombre_producto
""")
df_productos_agrupados.createOrReplaceTempView("ventas_por_producto")

# Ordenamos de mayor a menor unidades vendidas en cada franja y nos quedamos con el nº 1
df_top_productos = spark.sql("""
    SELECT
        tipo_ventana,
        franja_horaria,
        id_producto,
        nombre_producto,
        unidades_totales,
        euros_producto
    FROM (
        SELECT
            *,
            ROW_NUMBER() OVER (
                PARTITION BY tipo_ventana, franja_horaria
                ORDER BY unidades_totales DESC
            ) AS posicion
        FROM ventas_por_producto
    )
    WHERE posicion = 1
    ORDER BY tipo_ventana, franja_horaria
""")

print(">>> Muestra del producto más vendido por cada tramo de 1 HORA:")
df_top_productos.filter("tipo_ventana = '1_HORA'").show(12, truncate=False)

# -------------------------------------------------------------------------
# PASO 4: INTEGRACIÓN EMPRESARIAL - Guardar resultados en PostgreSQL (JDBC)
# -------------------------------------------------------------------------
print("\n==========================================================")
print("4. GUARDANDO RESULTADOS EN POSTGRESQL (INTEGRACIÓN JDBC)")
print("==========================================================")

url_jdbc = "jdbc:postgresql://mercadona_db:5432/mercadona_bi"
propiedades_db = {
    "user": "postgres",
    "password": "postgres",
    "driver": "org.postgresql.Driver"
}

df_resumen_ventas.write.jdbc(
    url=url_jdbc,
    table="resumen_ventas_tramo",
    mode="overwrite",
    properties=propiedades_db
)

df_top_productos.write.jdbc(
    url=url_jdbc,
    table="producto_mas_vendido_tramo",
    mode="overwrite",
    properties=propiedades_db
)

print(">>> ¡Tablas 'resumen_ventas_tramo' y 'producto_mas_vendido_tramo' guardadas con éxito en PostgreSQL!")
spark.stop()
