import pyodbc

# 1. Cadena de conexión estándar ODBC usando el driver oficial PostgreSQL Unicode
# Nos conectamos con el usuario 'empleado_tienda' (principio de mínimo privilegio)
cadena_odbc = (
    "DRIVER={PostgreSQL Unicode};"
    "SERVER=mercadona_postgres;"
    "PORT=5432;"
    "DATABASE=mercadona_bi;"
    "UID=empleado_tienda;"
    "PWD=tienda_pass;"
)

print("======================================================================")
print(" 1. CONEXIÓN MEDIANTE INTERFAZ ODBC (Driver: PostgreSQL Unicode)")
print("======================================================================")

# Usamos un bloque try/finally para asegurar el cierre de la conexión (Buena práctica)
conexion = None
try:
    conexion = pyodbc.connect(cadena_odbc)
    cursor = conexion.cursor()
    print("[OK] Conectado por ODBC a 'mercadona_bi' con el rol 'empleado_tienda'.\n")

    # 2. Consulta parametrizada (?) sobre la VISTA DEL NIVEL EXTERNO
    # Buscamos las franjas donde las unidades vendidas superan cierto umbral
    umbral_unidades = 900
    sql_vista = """
        SELECT franja_horaria, id_producto, nombre_producto,
               precio_venta, unidades_vendidas_tramo, stock_actual
        FROM vista_personal_tienda
        WHERE unidades_vendidas_tramo >= ?
        ORDER BY franja_horaria;
    """
    cursor.execute(sql_vista, (umbral_unidades,))
    filas = cursor.fetchall()

    print(f"--- Consulta Nivel Externo (vista_personal_tienda, ventas >= {umbral_unidades} uds) ---")
    print(f"{'Franja':<8} | {'ID':<8} | {'Producto':<30} | {'Precio':<7} | {'Vendidas':<8} | {'Stock':<6}")
    print("-" * 80)
    for f in filas:
        print(f"{f.franja_horaria:<8} | {f.id_producto:<8} | {f.nombre_producto:<30} | {f.precio_venta:>5.2f} € | {f.unidades_vendidas_tramo:>8} | {f.stock_actual:>6}")

    # 3. Comprobación de seguridad del Nivel Externo:
    # Intentamos leer la tabla conceptual 'productos_catalogo' (que tiene coste_proveedor)
    print("\n--- Prueba de seguridad: intento de leer 'productos_catalogo' (Nivel Conceptual) ---")
    try:
        cursor.execute("SELECT id_producto, coste_proveedor FROM productos_catalogo;")
    except pyodbc.Error as err:
        print("[BLOQUEADO POR POSTGRESQL] El rol 'empleado_tienda' no puede ver costes de proveedor:")
        print(f"  -> Detalle: {err.args[1].splitlines()[0]}")

finally:
    if conexion is not None:
        conexion.close()
        print("\n[OK] Conexión ODBC cerrada correctamente.")
