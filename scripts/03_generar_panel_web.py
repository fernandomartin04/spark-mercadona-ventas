import csv
import io
import json
import subprocess

print("Leyendo tablas desde PostgreSQL (mercadona_postgres)...")

def consultar_postgres(sql):
    cmd = [
        "docker", "exec", "mercadona_postgres",
        "psql", "-U", "postgres", "-d", "mercadona_bi",
        "--csv", "-c", sql
    ]
    resultado = subprocess.run(cmd, capture_output=True, text=True, check=True)
    lector = csv.DictReader(io.StringIO(resultado.stdout))
    return list(lector)

# 1. Extraemos las dos tablas generadas por Spark SQL en PostgreSQL
ventas_tramo = consultar_postgres(
    "SELECT tipo_ventana, franja_horaria, numero_ventas, recaudacion_euros, media_global_euros "
    "FROM resumen_ventas_tramo ORDER BY tipo_ventana, franja_horaria;"
)

top_productos = consultar_postgres(
    "SELECT tipo_ventana, franja_horaria, id_producto, nombre_producto, unidades_totales, euros_producto "
    "FROM producto_mas_vendido_tramo ORDER BY tipo_ventana, franja_horaria;"
)

# Unimos la información por (tipo_ventana, franja_horaria) para pasársela limpia al HTML
mapa_productos = {
    (fila["tipo_ventana"], fila["franja_horaria"]): fila
    for fila in top_productos
}

datos_combinados = []
for v in ventas_tramo:
    clave = (v["tipo_ventana"], v["franja_horaria"])
    prod = mapa_productos.get(clave, {})
    datos_combinados.append({
        "tipo_ventana": v["tipo_ventana"],
        "franja_horaria": v["franja_horaria"],
        "numero_ventas": int(v["numero_ventas"]),
        "recaudacion_euros": float(v["recaudacion_euros"]),
        "media_global_euros": float(v["media_global_euros"]),
        "id_producto": prod.get("id_producto", ""),
        "nombre_producto": prod.get("nombre_producto", ""),
        "unidades_totales": int(prod.get("unidades_totales", 0)),
        "euros_producto": float(prod.get("euros_producto", 0.0))
    })

datos_json = json.dumps(datos_combinados, ensure_ascii=False, indent=2)

html_content = f"""<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <title>Panel de Ventas Mercadona - Spark SQL + PostgreSQL</title>
    <style>
        body {{
            font-family: Arial, sans-serif;
            background-color: #f4f6f5;
            color: #222;
            margin: 0;
            padding: 25px;
        }}
        .contenedor {{
            max-width: 950px;
            margin: 0 auto;
            background: #ffffff;
            padding: 25px 30px;
            border-radius: 6px;
            border: 1px solid #dcdcdc;
        }}
        h1 {{
            color: #007a33;
            margin-top: 0;
            margin-bottom: 5px;
            font-size: 24px;
        }}
        .subtitulo {{
            color: #555;
            font-size: 14px;
            margin-bottom: 20px;
            padding-bottom: 12px;
            border-bottom: 2px solid #007a33;
        }}
        .filtros {{
            background-color: #eef5f0;
            padding: 15px;
            border-radius: 5px;
            border: 1px solid #c8dfd0;
            display: flex;
            gap: 25px;
            align-items: center;
            margin-bottom: 20px;
        }}
        .filtros label {{
            font-weight: bold;
            font-size: 14px;
            margin-right: 8px;
        }}
        .filtros select {{
            padding: 7px 12px;
            font-size: 14px;
            border: 1px solid #999;
            border-radius: 4px;
            background: #fff;
        }}
        .tarjetas {{
            display: grid;
            grid-template-columns: repeat(3, 1fr);
            gap: 15px;
            margin-bottom: 25px;
        }}
        .tarjeta {{
            border: 1px solid #d0d7de;
            border-radius: 5px;
            padding: 15px;
            background-color: #fafafa;
        }}
        .tarjeta h3 {{
            margin: 0 0 8px 0;
            font-size: 13px;
            color: #555;
            text-transform: uppercase;
        }}
        .tarjeta .valor-principal {{
            font-size: 22px;
            font-weight: bold;
            color: #007a33;
            margin-bottom: 5px;
        }}
        .tarjeta .detalle {{
            font-size: 13px;
            color: #444;
        }}
        h2 {{
            font-size: 17px;
            color: #222;
            margin-bottom: 10px;
        }}
        table {{
            width: 100%;
            border-collapse: collapse;
            font-size: 14px;
        }}
        th, td {{
            border: 1px solid #ccc;
            padding: 8px 10px;
            text-align: left;
        }}
        th {{
            background-color: #007a33;
            color: white;
        }}
        tr:nth-child(even) {{
            background-color: #f9f9f9;
        }}
        tr.seleccionada {{
            background-color: #d8f3dc !important;
            font-weight: bold;
        }}
        .nota-pie {{
            margin-top: 15px;
            font-size: 12px;
            color: #666;
            text-align: right;
        }}
    </style>
</head>
<body>

<div class="contenedor">
    <h1>Consulta de Ventas y Stock - Mercadona</h1>
    <div class="subtitulo">
        Datos procesados con <strong>Apache Spark SQL</strong> (50.000 ventas) y consultados desde <strong>PostgreSQL</strong> (<code>mercadona_bi</code>)
    </div>

    <div class="filtros">
        <div>
            <label for="selectVentana">Intervalo de tiempo:</label>
            <select id="selectVentana" onchange="cambiarVentana()">
                <option value="1_HORA">Tramos de 1 Hora</option>
                <option value="30_MIN">Tramos de 30 Minutos</option>
            </select>
        </div>

        <div>
            <label for="selectFranja">Tramo horario a consultar:</label>
            <select id="selectFranja" onchange="actualizarVista()"></select>
        </div>
    </div>

    <div class="tarjetas">
        <div class="tarjeta">
            <h3 id="tituloMedia">Venta Media (Por 1 Hora)</h3>
            <div class="valor-principal" id="valMedia">0,00 €</div>
            <div class="detalle">Media calculada entre todos los tramos del día</div>
        </div>

        <div class="tarjeta">
            <h3 id="tituloRecaudacion">Recaudación en el tramo</h3>
            <div class="valor-principal" id="valRecaudacion">0,00 €</div>
            <div class="detalle" id="valNumVentas">0 líneas de ticket registradas</div>
        </div>

        <div class="tarjeta">
            <h3 id="tituloTopProd">Producto más vendido en el tramo</h3>
            <div class="valor-principal" id="valProdNombre" style="font-size: 17px;">-</div>
            <div class="detalle" id="valProdDetalle">0 unidades vendidas (0,00 €)</div>
        </div>
    </div>

    <h2 id="tituloTabla">Desglose completo del día (haz clic en cualquier fila para seleccionarla)</h2>
    <table>
        <thead>
            <tr>
                <th>Franja Horaria</th>
                <th>Nº Ventas</th>
                <th>Recaudación Tramo (€)</th>
                <th>Venta Media Día (€)</th>
                <th>Producto Más Vendido</th>
                <th>Unidades</th>
                <th>Importe Producto (€)</th>
            </tr>
        </thead>
        <tbody id="tablaCuerpo"></tbody>
    </table>

    <div class="nota-pie">
        TPI 2 - Ampliación de Bases de Datos · Fernando Martín González
    </div>
</div>

<script>
    const DATOS = {datos_json};

    function formatearEuros(numero) {{
        return numero.toLocaleString('es-ES', {{ minimumFractionDigits: 2, maximumFractionDigits: 2 }}) + ' €';
    }}

    function cambiarVentana() {{
        const ventana = document.getElementById('selectVentana').value;
        const selectFranja = document.getElementById('selectFranja');
        selectFranja.innerHTML = '';

        const filtrados = DATOS.filter(d => d.tipo_ventana === ventana);
        filtrados.forEach(item => {{
            const opt = document.createElement('option');
            opt.value = item.franja_horaria;
            opt.textContent = item.franja_horaria + ' h';
            selectFranja.appendChild(opt);
        }});

        // Por defecto seleccionamos las 12:00 (hora punta)
        if (filtrados.some(d => d.franja_horaria === '12:00')) {{
            selectFranja.value = '12:00';
        }}

        actualizarVista();
    }}

    function seleccionarFila(franja) {{
        document.getElementById('selectFranja').value = franja;
        actualizarVista();
    }}

    function actualizarVista() {{
        const ventana = document.getElementById('selectVentana').value;
        const franjaElegida = document.getElementById('selectFranja').value;
        const etiquetaVentana = (ventana === '1_HORA') ? '1 Hora' : '30 Minutos';

        const filtrados = DATOS.filter(d => d.tipo_ventana === ventana);
        const actual = filtrados.find(d => d.franja_horaria === franjaElegida) || filtrados[0];

        if (!actual) return;

        document.getElementById('tituloMedia').textContent = 'Venta Media (Por ' + etiquetaVentana + ')';
        document.getElementById('valMedia').textContent = formatearEuros(actual.media_global_euros);

        document.getElementById('tituloRecaudacion').textContent = 'Recaudación Tramo (' + actual.franja_horaria + ' h)';
        document.getElementById('valRecaudacion').textContent = formatearEuros(actual.recaudacion_euros);
        document.getElementById('valNumVentas').textContent = actual.numero_ventas.toLocaleString('es-ES') + ' ventas en caja';

        document.getElementById('tituloTopProd').textContent = 'Más vendido (' + actual.franja_horaria + ' h)';
        document.getElementById('valProdNombre').textContent = actual.nombre_producto;
        document.getElementById('valProdDetalle').textContent =
            actual.unidades_totales.toLocaleString('es-ES') + ' unidades (' + formatearEuros(actual.euros_producto) + ')';

        const tbody = document.getElementById('tablaCuerpo');
        tbody.innerHTML = '';

        filtrados.forEach(fila => {{
            const tr = document.createElement('tr');
            tr.style.cursor = 'pointer';
            if (fila.franja_horaria === franjaElegida) {{
                tr.className = 'seleccionada';
            }}
            tr.onclick = () => seleccionarFila(fila.franja_horaria);

            tr.innerHTML = `
                <td>${{fila.franja_horaria}} h</td>
                <td>${{fila.numero_ventas.toLocaleString('es-ES')}}</td>
                <td>${{formatearEuros(fila.recaudacion_euros)}}</td>
                <td>${{formatearEuros(fila.media_global_euros)}}</td>
                <td>${{fila.nombre_producto}} (<code>${{fila.id_producto}}</code>)</td>
                <td>${{fila.unidades_totales.toLocaleString('es-ES')}} uds</td>
                <td>${{formatearEuros(fila.euros_producto)}}</td>
            `;
            tbody.appendChild(tr);
        }});
    }}

    cambiarVentana();
</script>

</body>
</html>
"""

with open("panel_mercadona.html", "w", encoding="utf-8") as f:
    f.write(html_content)

print("¡Archivo 'panel_mercadona.html' generado correctamente con los datos de PostgreSQL!")
