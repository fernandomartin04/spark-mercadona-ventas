import csv
import random
from datetime import datetime, timedelta

# Semilla fija para que siempre salgan los mismos datos si repetimos la prueba
random.seed(42)

# Catálogo realista de productos típicos de Mercadona (ID, Nombre, Precio en €)
PRODUCTOS = [
    ("PROD_01", "Leche Entera Hacendado 1L", 0.95),
    ("PROD_02", "Guacamole Hacendado 200g", 1.75),
    ("PROD_03", "Pechuga de Pollo Fileteada 500g", 4.20),
    ("PROD_04", "Aceite de Oliva Virgen Extra 1L", 8.50),
    ("PROD_05", "Cerveza Steinburg Pack 12", 3.60),
    ("PROD_06", "Huevos Camperos Docena", 2.65),
    ("PROD_07", "Pan de Molde Blanco Hacendado", 1.15),
    ("PROD_08", "Atun Claro en Aceite de Oliva Pack 6", 4.95),
    ("PROD_09", "Yogur Griego Natural Pack 6", 1.60),
    ("PROD_10", "Pizza Jamon y Queso Hacendado", 2.90),
    ("PROD_11", "Cafe Molido Natural Mezcla 250g", 2.10),
    ("PROD_12", "Salmorejo Fresco Hacendado 1L", 2.15),
    ("PROD_13", "Papel Higienico Doble Rollo 12u", 4.10),
    ("PROD_14", "Queso Lonchas Havarti Hacendado", 2.25),
    ("PROD_15", "Patatas Fritas Con Sal 150g", 1.10)
]

# Tiendas de Mercadona en Sevilla
TIENDAS = [
    "MERC_SEV_MACARENA",
    "MERC_SEV_NERVION",
    "MERC_SEV_TRIANA",
    "MERC_SEV_LOS_REMEDIOS",
    "MERC_SEV_BAMI"
]

NUM_VENTAS = 50000
ARCHIVO_SALIDA = "data/ventas_mercadona.csv"

print(f"Generando {NUM_VENTAS} registros de ventas en {ARCHIVO_SALIDA}...")

fecha_base = datetime(2026, 10, 24, 9, 0, 0)  # Apertura a las 09:00

with open(ARCHIVO_SALIDA, mode="w", newline="", encoding="utf-8") as f:
    escritor = csv.writer(f)
    # Cabecera clara y sencilla
    escritor.writerow([
        "id_venta",
        "fecha_hora",
        "id_tienda",
        "id_producto",
        "nombre_producto",
        "cantidad",
        "precio_unitario",
        "importe_total"
    ])

    for id_venta in range(1, NUM_VENTAS + 1):
        # Elegimos la hora del día (de 9:00 a 20:59, 12 horas de apertura)
        # Ponemos más peso en horas punta (11h-14h y 18h-20h) para que las medias sean interesantes
        hora_offset = random.choices(
            population=[0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11],
            weights=[5, 8, 12, 15, 14, 7, 5, 6, 10, 14, 12, 6],
            k=1
        )[0]
        minuto = random.randint(0, 59)
        segundo = random.randint(0, 59)

        momento = fecha_base + timedelta(hours=hora_offset, minutes=minuto, seconds=segundo)
        fecha_str = momento.strftime("%Y-%m-%d %H:%M:%S")

        tienda = random.choice(TIENDAS)

        # Según la hora, algunos productos se venden más (para que cambie el top ventas de forma realista)
        hora_actual = momento.hour
        if hora_actual < 12:
            # Por la mañana triunfan leche, café, pan y huevos
            pesos_prod = [18, 5, 6, 4, 3, 14, 15, 5, 8, 3, 14, 3, 4, 5, 3]
        elif hora_actual < 16:
            # Al mediodía triunfan cerveza, guacamole, pollo y salmorejo
            pesos_prod = [6, 18, 16, 5, 20, 6, 4, 7, 5, 8, 3, 15, 3, 6, 10]
        else:
            # Por la tarde triunfan pizzas, yogures, patatas, queso y leche
            pesos_prod = [12, 10, 10, 4, 12, 8, 6, 8, 15, 18, 4, 5, 6, 14, 16]

        id_prod, nombre_prod, precio = random.choices(PRODUCTOS, weights=pesos_prod, k=1)[0]
        cantidad = random.choices([1, 2, 3, 4, 6], weights=[50, 30, 12, 5, 3], k=1)[0]
        importe_total = round(cantidad * precio, 2)

        escritor.writerow([
            id_venta,
            fecha_str,
            tienda,
            id_prod,
            nombre_prod,
            cantidad,
            precio,
            importe_total
        ])

print("¡Archivo CSV generado correctamente!")
