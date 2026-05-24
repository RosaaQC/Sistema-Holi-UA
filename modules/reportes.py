"""
================================================================
MÓDULO REPORTES - Generación de PDFs ejecutivos
================================================================
Proyecto: Sistema de Predicción de Demanda - Supermercados Holi
Descripción: Construye reportes en PDF con métricas y análisis
================================================================
"""

from io import BytesIO
from datetime import datetime

from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.lib.colors import HexColor, white, black
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_JUSTIFY
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    PageBreak, Image
)


# ================================================================
# PALETA DE COLORES CORPORATIVA
# ================================================================
COLOR_PRIMARIO = HexColor("#667eea")     # Morado/Azul
COLOR_SECUNDARIO = HexColor("#764ba2")   # Morado oscuro
COLOR_TEXTO = HexColor("#1a1a2e")        # Casi negro
COLOR_GRIS = HexColor("#f0f0f0")         # Gris claro para fondos
COLOR_VERDE = HexColor("#10b981")        # Para destacar positivo
COLOR_NARANJA = HexColor("#f59e0b")      # Para advertencias


# ================================================================
# FUNCIÓN AUXILIAR: ESTILOS DE TEXTO
# ================================================================
def crear_estilos():
    """Crea los estilos de párrafo para el PDF."""
    estilos = getSampleStyleSheet()

    estilos.add(ParagraphStyle(
        name="TituloPrincipal",
        fontSize=24,
        textColor=COLOR_PRIMARIO,
        alignment=TA_CENTER,
        spaceAfter=20,
        fontName="Helvetica-Bold",
    ))

    estilos.add(ParagraphStyle(
        name="Subtitulo",
        fontSize=16,
        textColor=COLOR_SECUNDARIO,
        spaceAfter=12,
        spaceBefore=12,
        fontName="Helvetica-Bold",
    ))

    estilos.add(ParagraphStyle(
        name="TextoNormal",
        fontSize=11,
        textColor=COLOR_TEXTO,
        alignment=TA_JUSTIFY,
        spaceAfter=8,
        leading=15,
        fontName="Helvetica",
    ))

    estilos.add(ParagraphStyle(
        name="Etiqueta",
        fontSize=10,
        textColor=HexColor("#666666"),
        alignment=TA_CENTER,
        fontName="Helvetica",
    ))

    return estilos


# ================================================================
# FUNCIÓN AUXILIAR: TABLA DE KPIs
# ================================================================
def crear_tabla_kpis(kpis):
    """Crea una tabla visual con los KPIs principales."""
    datos = [
        ["💰 Ventas Totales", f"S/ {kpis['ventas_totales']:,.2f}"],
        ["📦 Productos Únicos", f"{kpis['productos_unicos']}"],
        ["🧾 Transacciones", f"{kpis['transacciones']:,}"],
        ["🎫 Ticket Promedio", f"S/ {kpis['ticket_promedio']:,.2f}"],
        ["📊 Unidades Vendidas", f"{kpis['unidades_vendidas']:,}"],
        ["🏢 Sucursales Activas", f"{kpis['sucursales_activas']}"],
        ["📅 Días de Operación", f"{kpis['dias_operacion']} días"],
    ]

    tabla = Table(datos, colWidths=[8 * cm, 7 * cm])
    tabla.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (0, -1), COLOR_GRIS),
        ("TEXTCOLOR", (0, 0), (-1, -1), COLOR_TEXTO),
        ("ALIGN", (0, 0), (0, -1), "LEFT"),
        ("ALIGN", (1, 0), (1, -1), "RIGHT"),
        ("FONTNAME", (0, 0), (0, -1), "Helvetica-Bold"),
        ("FONTNAME", (1, 0), (1, -1), "Helvetica"),
        ("FONTSIZE", (0, 0), (-1, -1), 11),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 10),
        ("TOPPADDING", (0, 0), (-1, -1), 10),
        ("GRID", (0, 0), (-1, -1), 0.5, HexColor("#cccccc")),
    ]))

    return tabla


# ================================================================
# FUNCIÓN AUXILIAR: TABLA DE TOP PRODUCTOS
# ================================================================
def crear_tabla_top_productos(df_top):
    """Crea una tabla con los Top productos."""
    datos = [["#", "Producto", "Ventas (S/)"]]

    for i, row in df_top.iterrows():
        datos.append([
            str(i + 1),
            str(row["PRODUCTO"])[:35],
            f"S/ {row['TOTAL_VENTA']:,.2f}",
        ])

    tabla = Table(datos, colWidths=[1.5 * cm, 10 * cm, 4 * cm])
    tabla.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), COLOR_PRIMARIO),
        ("TEXTCOLOR", (0, 0), (-1, 0), white),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("ALIGN", (0, 0), (-1, 0), "CENTER"),
        ("ALIGN", (0, 1), (0, -1), "CENTER"),
        ("ALIGN", (1, 1), (1, -1), "LEFT"),
        ("ALIGN", (2, 1), (2, -1), "RIGHT"),
        ("FONTNAME", (0, 1), (-1, -1), "Helvetica"),
        ("FONTSIZE", (0, 0), (-1, -1), 10),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [white, COLOR_GRIS]),
        ("GRID", (0, 0), (-1, -1), 0.5, HexColor("#cccccc")),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
        ("TOPPADDING", (0, 0), (-1, -1), 8),
    ]))

    return tabla


# ================================================================
# FUNCIÓN AUXILIAR: TABLA DE RESUMEN ABC
# ================================================================
def crear_tabla_abc(resumen_abc):
    """Crea una tabla con el resumen de clasificación ABC."""
    datos = [["Clasificación", "Productos", "Ventas Totales", "Porcentaje"]]

    colores_clase = {"A": COLOR_VERDE, "B": COLOR_NARANJA, "C": HexColor("#9ca3af")}

    for _, row in resumen_abc.iterrows():
        datos.append([
            f"Categoría {row['Clasificación']}",
            str(int(row["Productos"])),
            f"S/ {row['Ventas_Totales']:,.2f}",
            f"{row['Porcentaje']:.1f}%",
        ])

    tabla = Table(datos, colWidths=[4 * cm, 3 * cm, 5 * cm, 3 * cm])
    tabla.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), COLOR_PRIMARIO),
        ("TEXTCOLOR", (0, 0), (-1, 0), white),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("ALIGN", (0, 0), (-1, -1), "CENTER"),
        ("FONTNAME", (0, 1), (-1, -1), "Helvetica"),
        ("FONTSIZE", (0, 0), (-1, -1), 10),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [white, COLOR_GRIS]),
        ("GRID", (0, 0), (-1, -1), 0.5, HexColor("#cccccc")),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 10),
        ("TOPPADDING", (0, 0), (-1, -1), 10),
    ]))

    return tabla


# ================================================================
# FUNCIÓN PRINCIPAL: GENERAR PDF EJECUTIVO
# ================================================================
def generar_pdf_ejecutivo(kpis, df_top_productos, resumen_abc_df, log_etl=None):
    """
    Genera un reporte PDF ejecutivo con todo el análisis.

    Parámetros:
        kpis: diccionario con KPIs (de calcular_kpis)
        df_top_productos: DataFrame con top productos
        resumen_abc_df: DataFrame con resumen ABC
        log_etl: diccionario con el log del ETL (opcional)

    Retorna:
        BytesIO listo para descargar
    """
    buffer = BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=2 * cm,
        leftMargin=2 * cm,
        topMargin=2 * cm,
        bottomMargin=2 * cm,
    )

    elementos = []
    estilos = crear_estilos()

    elementos.append(Paragraph(
        "🛒 Supermercados Holi",
        estilos["TituloPrincipal"]
    ))
    elementos.append(Paragraph(
        "Reporte Ejecutivo - Análisis de Ventas 2025",
        estilos["Subtitulo"]
    ))
    elementos.append(Spacer(1, 0.3 * cm))
    elementos.append(Paragraph(
        f"Generado el: {datetime.now().strftime('%d/%m/%Y %H:%M')}",
        estilos["Etiqueta"]
    ))
    elementos.append(Spacer(1, 1 * cm))

    elementos.append(Paragraph(
        "📊 Indicadores Clave del Negocio (KPIs)",
        estilos["Subtitulo"]
    ))
    elementos.append(Paragraph(
        f"Período analizado: <b>{kpis['fecha_inicio'].strftime('%d/%m/%Y')}</b> "
        f"al <b>{kpis['fecha_fin'].strftime('%d/%m/%Y')}</b>",
        estilos["TextoNormal"]
    ))
    elementos.append(Spacer(1, 0.3 * cm))
    elementos.append(crear_tabla_kpis(kpis))
    elementos.append(Spacer(1, 0.8 * cm))

    elementos.append(Paragraph(
        "🏆 Top 10 Productos por Ventas",
        estilos["Subtitulo"]
    ))
    elementos.append(Paragraph(
        "Listado de los productos que más aportan a las ventas totales de la cadena.",
        estilos["TextoNormal"]
    ))
    elementos.append(Spacer(1, 0.3 * cm))
    elementos.append(crear_tabla_top_productos(df_top_productos.head(10)))
    elementos.append(Spacer(1, 0.8 * cm))

    elementos.append(PageBreak())

    elementos.append(Paragraph(
        "📈 Análisis ABC de Productos",
        estilos["Subtitulo"]
    ))
    elementos.append(Paragraph(
        "El análisis ABC clasifica los productos según su aporte a las ventas, "
        "siguiendo el principio de Pareto (80/20). Esto permite priorizar la "
        "gestión de inventario y las decisiones comerciales.",
        estilos["TextoNormal"]
    ))
    elementos.append(Spacer(1, 0.3 * cm))
    elementos.append(crear_tabla_abc(resumen_abc_df))
    elementos.append(Spacer(1, 0.5 * cm))

    elementos.append(Paragraph(
        "<b>Interpretación:</b>",
        estilos["TextoNormal"]
    ))
    elementos.append(Paragraph(
        "• <b>Categoría A</b>: Productos estrella que generan el 80% de las ventas. "
        "Requieren stock prioritario y reposición frecuente.",
        estilos["TextoNormal"]
    ))
    elementos.append(Paragraph(
        "• <b>Categoría B</b>: Productos importantes que aportan el 15% de las ventas. "
        "Requieren atención regular.",
        estilos["TextoNormal"]
    ))
    elementos.append(Paragraph(
        "• <b>Categoría C</b>: Productos de baja rotación que aportan solo el 5%. "
        "Pueden ser candidatos a descontinuar o promocionar.",
        estilos["TextoNormal"]
    ))
    elementos.append(Spacer(1, 0.8 * cm))

    if log_etl:
        elementos.append(Paragraph(
            "🧹 Proceso ETL Aplicado",
            estilos["Subtitulo"]
        ))
        elementos.append(Paragraph(
            f"Se procesaron <b>{log_etl.get('registros_iniciales', 0):,}</b> "
            f"registros, eliminándose <b>{log_etl.get('registros_eliminados', 0)}</b> "
            f"registros problemáticos. Resultando en un dataset final de "
            f"<b>{log_etl.get('registros_finales', 0):,}</b> transacciones válidas.",
            estilos["TextoNormal"]
        ))
        elementos.append(Spacer(1, 0.3 * cm))

        datos_etl = [
            ["Acción de Limpieza", "Cantidad"],
            ["Duplicados eliminados", str(log_etl.get("duplicados_eliminados", 0))],
            ["Fechas inválidas eliminadas", str(log_etl.get("fechas_invalidas_eliminadas", 0))],
            ["Categorías normalizadas", str(log_etl.get("categorias_normalizadas", 0))],
            ["Sucursales normalizadas", str(log_etl.get("sucursales_normalizadas", 0))],
            ["Métodos de pago normalizados", str(log_etl.get("metodos_pago_normalizados", 0))],
            ["Precios imputados", str(log_etl.get("nulos_precio_imputados", 0))],
            ["Stock imputado", str(log_etl.get("nulos_stock_imputados", 0))],
            ["Cantidades inválidas eliminadas", str(log_etl.get("cantidades_invalidas_eliminadas", 0))],
            ["Stock negativo corregido", str(log_etl.get("stock_negativo_corregido", 0))],
        ]

        tabla_etl = Table(datos_etl, colWidths=[10 * cm, 5 * cm])
        tabla_etl.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), COLOR_PRIMARIO),
            ("TEXTCOLOR", (0, 0), (-1, 0), white),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ("ALIGN", (1, 0), (1, -1), "CENTER"),
            ("FONTNAME", (0, 1), (-1, -1), "Helvetica"),
            ("FONTSIZE", (0, 0), (-1, -1), 10),
            ("ROWBACKGROUNDS", (0, 1), (-1, -1), [white, COLOR_GRIS]),
            ("GRID", (0, 0), (-1, -1), 0.5, HexColor("#cccccc")),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
            ("TOPPADDING", (0, 0), (-1, -1), 8),
        ]))
        elementos.append(tabla_etl)
        elementos.append(Spacer(1, 0.8 * cm))

    elementos.append(Spacer(1, 1 * cm))
    elementos.append(Paragraph(
        "─" * 60,
        estilos["Etiqueta"]
    ))
    elementos.append(Paragraph(
        "Sistema de Análisis Predictivo - Supermercados Holi",
        estilos["Etiqueta"]
    ))
    elementos.append(Paragraph(
        "Proyecto académico - Big Data - VIII Ciclo - 2026",
        estilos["Etiqueta"]
    ))

    doc.build(elementos)
    buffer.seek(0)
    return buffer
