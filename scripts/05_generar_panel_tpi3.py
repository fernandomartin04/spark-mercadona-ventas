# ============================================================================
# TPI 3 - Ampliación de Bases de Datos (Tema 6)
# Archivo: scripts/05_generar_panel_tpi3.py
# Propósito: Generar una página HTML muy sencilla (panel_arquitectura_tpi3.html)
#            que muestra visualmente las dos vistas del Nivel Externo
#            (Personal de Tienda vs. Dirección) y los cambios de JDBC/Hibernate.
# ============================================================================

import csv
import io
import subprocess

print("Consultando las vistas del Nivel Externo en PostgreSQL...")

def consultar_postgres(sql):
    cmd = [
        "docker", "exec", "mercadona_postgres",
        "psql", "-U", "postgres", "-d", "mercadona_bi",
        "--csv", "-c", sql
    ]
    res = subprocess.run(cmd, capture_output=True, text=True, check=True)
    return list(csv.DictReader(io.StringIO(res.stdout)))

# 1. Leemos la Vista 1: Personal de Tienda (sin costes ni márgenes)
vista_tienda = consultar_postgres("SELECT * FROM vista_personal_tienda;")

# 2. Leemos la Vista 2: Dirección Financiera (con coste_proveedor y beneficio neto)
vista_direccion = consultar_postgres("SELECT * FROM vista_direccion_mercadona;")

# 3. Leemos la tabla de reposiciones (incluyendo el pedido insertado por JDBC)
reposiciones = consultar_postgres(
    "SELECT r.id_reposicion, r.id_tienda, t.barrio, r.id_producto, p.nombre_producto, "
    "r.unidades_reponer, r.franja_horaria "
    "FROM reposiciones_stock r "
    "JOIN tiendas t ON r.id_tienda = t.id_tienda "
    "JOIN productos_catalogo p ON r.id_producto = p.id_producto "
    "ORDER BY r.id_reposicion;"
)

# Generamos las filas HTML de cada tabla de forma directa y sencilla
filas_tienda_html = ""
for f in vista_tienda:
    filas_tienda_html += f"""
        <tr>
            <td><b>{f['franja_horaria']}</b></td>
            <td>{f['id_producto']}</td>
            <td>{f['nombre_producto']}</td>
            <td>{f['categoria']}</td>
            <td>{float(f['precio_venta']):.2f} €</td>
            <td>{f['unidades_vendidas_tramo']}</td>
            <td><b>{f['stock_actual']} uds</b></td>
        </tr>"""

filas_direccion_html = ""
for f in vista_direccion:
    filas_direccion_html += f"""
        <tr>
            <td><b>{f['franja_horaria']}</b></td>
            <td>{f['nombre_producto']}</td>
            <td>{f['unidades_totales']}</td>
            <td>{float(f['precio_venta']):.2f} €</td>
            <td class="confidencial">{float(f['coste_proveedor']):.2f} €</td>
            <td class="confidencial">{float(f['margen_unitario_eur']):.2f} €</td>
            <td class="beneficio"><b>{float(f['beneficio_neto_tramo_eur']):.2f} €</b></td>
        </tr>"""

filas_repo_html = ""
for r in reposiciones:
    filas_repo_html += f"""
        <tr>
            <td>#{r['id_reposicion']}</td>
            <td>{r['id_tienda']} ({r['barrio']})</td>
            <td>{r['id_producto']} - {r['nombre_producto']}</td>
            <td><b>+{r['unidades_reponer']} uds</b></td>
            <td>{r['franja_horaria']}</td>
        </tr>"""

html = f"""<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <title>Mercadona TPI 3 - Arquitectura de 3 Niveles, JDBC, ODBC y Hibernate</title>
    <style>
        body {{
            font-family: Arial, sans-serif;
            background-color: #f4f6f5;
            color: #222;
            margin: 0;
            padding: 20px;
        }}
        .contenedor {{
            max-width: 980px;
            margin: 0 auto;
            background: #fff;
            padding: 22px 28px;
            border-radius: 8px;
            border-top: 6px solid #00754a;
            box-shadow: 0 2px 6px rgba(0,0,0,0.08);
        }}
        h1 {{
            color: #00754a;
            font-size: 22px;
            margin: 0 0 6px 0;
        }}
        .subtitulo {{
            color: #555;
            font-size: 14px;
            margin-bottom: 18px;
        }}
        h2 {{
            color: #082B66;
            font-size: 16px;
            margin-top: 22px;
            margin-bottom: 8px;
            border-bottom: 2px solid #e5e7eb;
            padding-bottom: 4px;
        }}
        .etiqueta {{
            display: inline-block;
            font-size: 12px;
            padding: 2px 8px;
            border-radius: 4px;
            margin-left: 8px;
            font-weight: normal;
        }}
        .etiqueta-odbc {{ background: #e0f2fe; color: #0369a1; }}
        .etiqueta-jdbc {{ background: #fef3c7; color: #b45309; }}
        .etiqueta-orm  {{ background: #dcfce7; color: #15803d; }}
        table {{
            width: 100%;
            border-collapse: collapse;
            font-size: 13px;
            margin-bottom: 14px;
        }}
        th {{
            background: #00754a;
            color: #fff;
            text-align: left;
            padding: 7px 9px;
        }}
        td {{
            padding: 6px 9px;
            border-bottom: 1px solid #e5e7eb;
        }}
        tr:nth-child(even) {{ background: #f9fafb; }}
        .confidencial {{ color: #b91c1c; background: #fef2f2; }}
        .beneficio {{ color: #00754a; background: #ecfdf5; }}
    </style>
</head>
<body>
<div class="contenedor">
    <h1>Mercadona Sevilla — Arquitectura de Tres Niveles (TPI 3)</h1>
    <div class="subtitulo">
        Demostración del <b>Nivel Externo</b> (vistas diferenciadas por rol) y actualizaciones mediante <b>ODBC, JDBC y ORM Hibernate</b> sobre PostgreSQL (<code>mercadona_bi</code>).
    </div>

    <h2>1. Vista Nivel Externo: Personal de Tienda (<code>vista_personal_tienda</code>)
        <span class="etiqueta etiqueta-odbc">Consultada vía ODBC · Rol: empleado_tienda (Coste oculto)</span>
        <span class="etiqueta etiqueta-orm">Stock PROD_05 actualizado a 370 por Hibernate</span>
    </h2>
    <table>
        <thead>
            <tr>
                <th>Franja</th>
                <th>ID</th>
                <th>Producto Estrella</th>
                <th>Categoría</th>
                <th>Precio Venta</th>
                <th>Vendidas (1h)</th>
                <th>Stock Tienda</th>
            </tr>
        </thead>
        <tbody>{filas_tienda_html}
        </tbody>
    </table>

    <h2>2. Vista Nivel Externo: Dirección Financiera (<code>vista_direccion_mercadona</code>)
        <span class="etiqueta etiqueta-jdbc">Consultada vía JDBC · Incluye Coste Proveedor y Beneficio Neto</span>
    </h2>
    <table>
        <thead>
            <tr>
                <th>Franja</th>
                <th>Producto Estrella</th>
                <th>Unidades</th>
                <th>Precio Venta</th>
                <th>Coste Prov. (Confidencial)</th>
                <th>Margen / Ud.</th>
                <th>Beneficio Neto (1h)</th>
            </tr>
        </thead>
        <tbody>{filas_direccion_html}
        </tbody>
    </table>

    <h2>3. Pedidos de Reposición Registrados (<code>reposiciones_stock</code>)
        <span class="etiqueta etiqueta-jdbc">Último pedido (#5 Triana) insertado con Transacción ACID en JDBC</span>
    </h2>
    <table>
        <thead>
            <tr>
                <th>ID Pedido</th>
                <th>Tienda (Sevilla)</th>
                <th>Producto</th>
                <th>Unidades Repuestas</th>
                <th>Franja</th>
            </tr>
        </thead>
        <tbody>{filas_repo_html}
        </tbody>
    </table>
</div>
</body>
</html>
"""

archivo_salida = "panel_arquitectura_tpi3.html"
with open(archivo_salida, "w", encoding="utf-8") as f:
    f.write(html)

print(f"[OK] Panel web generado en: {archivo_salida}")
