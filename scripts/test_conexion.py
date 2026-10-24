from pyspark.sql import SparkSession

spark = SparkSession.builder \
    .appName("TestPostgresConnection") \
    .config("spark.jars", "/app/jars/postgresql-42.7.4.jar") \
    .getOrCreate()

print(">>> Conectando con PostgreSQL desde Spark...")
df = spark.read \
    .format("jdbc") \
    .option("url", "jdbc:postgresql://mercadona_db:5432/mercadona_bi") \
    .option("dbtable", "control_cargas") \
    .option("user", "postgres") \
    .option("password", "postgres") \
    .option("driver", "org.postgresql.Driver") \
    .load()

print(">>> Esquema de la tabla control_cargas:")
df.printSchema()
print(">>> Filas encontradas:", df.count())
print(">>> ¡CONEXIÓN PERFECTA ENTRE SPARK Y POSTGRESQL!")

spark.stop()
