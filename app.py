"""
================================================================
SISTEMA DE PREDICCIÓN DE DEMANDA - SUPERMERCADOS HOLI
================================================================
Dashboard principal con ETL integrado, análisis y predicción
================================================================
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import base64
import warnings
warnings.filterwarnings("ignore")

BACKGROUND_IMAGE_PATH = "modules/holi_fondo.png"
LOGO_IMAGE_PATH = "modules/holilogo.png"
PERSONAJE_IMAGE_PATH = "modules/personajeloguin.png"

# Importar módulos propios
from modules.etl import (
    validar_columnas,
    diagnosticar_dataset,
    aplicar_etl,
)
from modules.analisis import (
    calcular_kpis,
    analisis_abc,
    resumen_abc,
    analisis_rotacion,
    top_productos,
    ventas_por_sucursal,
    ventas_por_categoria,
    analisis_temporal,
    ventas_por_metodo_pago,
)
from modules.prediccion import (
    PROPHET_DISPONIBLE,
    predecir_demanda,
    obtener_prediccion_futura,
    resumen_prediccion,
)
from modules.reportes import generar_pdf_ejecutivo


# ================================================================
# CONFIGURACIÓN GENERAL DE LA APP
# ================================================================
st.set_page_config(
    page_title="Sistema Predictivo - Holi",
    layout="wide",
    page_icon=None,
    initial_sidebar_state="expanded",
)


def get_base64_image(path):
    if not path:
        return None
    try:
        with open(path, "rb") as f:
            return base64.b64encode(f.read()).decode()
    except FileNotFoundError:
        return None


# ================================================================
# ESTILOS PERSONALIZADOS
# ================================================================
image_base64 = get_base64_image(BACKGROUND_IMAGE_PATH)
logo_base64 = get_base64_image(LOGO_IMAGE_PATH)
personaje_base64 = get_base64_image(PERSONAJE_IMAGE_PATH)
# Construir el CSS del fondo dinámicamente con la imagen real
if image_base64:
    fondo_estilo = f"""
        background:
            linear-gradient(135deg, rgba(255, 240, 220, 0.35), rgba(255, 220, 180, 0.35)),
            url("data:image/png;base64,{image_base64}");
        background-size: cover;
        background-position: center;
        background-attachment: fixed;
    """
else:
    fondo_estilo = """
        background: radial-gradient(circle at top left, #ffe3c0 0%, #ffd09b 24%, #ffe5cd 56%, #fff2e9 100%);
        background-attachment: fixed;
    """

background_css = f"""
<style>
    /* FONDO PRINCIPAL */
    .stApp {{
        {fondo_estilo}
        color: #4a3f35;
        min-height: 100vh;
    }}

    /* HERO CARD */
    .hero-card {{
        max-width: 1080px;
        margin: 0 auto 28px auto;
        padding: 30px 34px;
        background: rgba(255, 245, 236, 0.96);
        border: 1px solid rgba(219, 160, 106, 0.22);
        border-radius: 34px;
        box-shadow: 0 26px 60px rgba(0, 0, 0, 0.08);
    }}
    .hero-title {{
        font-size: 3.2rem;
        font-weight: 800;
        line-height: 1.05;
        color: #7c3d14;
        margin: 0;
        letter-spacing: 0.03em;
        font-family: Georgia, serif;
    }}
    .hero-subtitle {{
        font-size: 1.8rem;
        margin-top: 12px;
        color: #d66815;
        font-style: italic;
        font-family: 'Segoe Script', cursive;
    }}
    .hero-note {{
        margin-top: 18px;
        display: inline-block;
        padding: 10px 16px;
        background: rgba(255, 231, 214, 0.85);
        color: #6d3b1a;
        border-radius: 22px;
        border: 1px solid rgba(235, 181, 130, 0.3);
        font-size: 0.95rem;
    }}

    /* TARJETAS KPI */
    .tarjeta-kpi {{
        background: linear-gradient(135deg, #FF9E0F 0%, #D35400 100%) !important;
        padding: 22px;
        border-radius: 22px;
        color: white !important;
        text-align: center;
        box-shadow: 0 16px 35px rgba(0, 0, 0, 0.15);
        transition: transform 0.28s ease;
    }}
    .tarjeta-kpi:hover {{
        transform: translateY(-6px);
    }}
    .kpi-valor {{ font-size: 32px; font-weight: 700; color: white !important; }}
    .kpi-etiqueta {{ font-size: 14px; opacity: 0.95; color: white !important; }}

    /* SIDEBAR */
    section[data-testid="stSidebar"] > div {{
        background: rgba(255, 216, 169, 0.96) !important;
    }}
    section[data-testid="stSidebar"] * {{
        color: #5e3b1a !important;
    }}
    .sidebar-title {{
        font-size: 1.55rem;
        font-weight: 800;
        margin-bottom: 18px;
        color: #7b3e1b !important;
    }}

    /* CONTENEDOR PRINCIPAL */
    .block-container {{
        backdrop-filter: blur(8px);
        background: rgba(255, 255, 255, 0.88) !important;
        border-radius: 30px;
        padding: 30px !important;
        margin-top: 20px !important;
    }}

    /* TÍTULOS Y TEXTO */
    h1, h2, h3, h4, h5, h6 {{
        color: #7b3e1b !important;
    }}

    /* LOGO TOP RIGHT */
    .logo-top-right {{
        position: fixed;
        top: 18px;
        right: 24px;
        z-index: 999;
        width: 110px;
        height: 110px;
        padding: 8px;
        border-radius: 50%;
        background: rgba(255, 250, 242, 0.95);
        border: 2px solid rgba(255, 158, 15, 0.4);
        box-shadow: 0 12px 28px rgba(0, 0, 0, 0.15);
        display: flex;
        align-items: center;
        justify-content: center;
    }}
    .logo-top-right img {{
        max-width: 100%;
        max-height: 100%;
        object-fit: contain;
        border-radius: 50%;
    }}

    /* OCULTAR menú y banner Deploy */
    #MainMenu {{ visibility: hidden; }}
    header[data-testid="stHeader"] {{ background: transparent !important; }}

    /* BOTONES */
    .stButton > button {{
        background: linear-gradient(135deg, #FF9E0F, #D35400) !important;
        color: white !important;
        border: none !important;
        border-radius: 18px !important;
        font-weight: 600 !important;
        padding: 10px 24px !important;
    }}
    .stButton > button:hover {{
        transform: translateY(-2px);
        box-shadow: 0 8px 20px rgba(211, 84, 0, 0.3);
    }}
</style>
"""

st.markdown(background_css, unsafe_allow_html=True)

if logo_base64:
    st.markdown(
        f"""
        <div class='logo-top-right'>
            <img src='data:image/png;base64,{logo_base64}' alt='Logo Holi' />
        </div>
        """,
        unsafe_allow_html=True,
    )

# ================================================================
# PANTALLA DE BIENVENIDA (SPLASH)
# ================================================================
if "iniciado" not in st.session_state:
    st.session_state.iniciado = False

if not st.session_state.iniciado:
    st.markdown(
        """
        <style>
            .block-container {
                background: transparent !important;
                backdrop-filter: none !important;
                box-shadow: none !important;
            }
            @keyframes flotar {
                0%   { transform: translateY(0px); }
                50%  { transform: translateY(-16px); }
                100% { transform: translateY(0px); }
            }
            .welcome-wrap {
                display: flex;
                flex-direction: column;
                align-items: center;
                justify-content: center;
                min-height: 78vh;
                text-align: center;
            }
            .welcome-floating {
                animation: flotar 3.6s ease-in-out infinite;
            }
            .welcome-title {
                font-size: 8.5rem;
                font-weight: 800;
                color: #7c3d14;
                margin: 0;
                letter-spacing: 0.03em;
                font-family: Georgia, serif;
                text-shadow: 0 6px 22px rgba(0, 0, 0, 0.28);
            }
            .welcome-subtitle {
                font-size: 4.5rem;
                margin-top: 10px;
                color: #d66815;
                font-style: italic;
                font-family: 'Segoe Script', cursive;
                text-shadow: 0 4px 16px rgba(0, 0, 0, 0.2);
            }
            .welcome-note {
                margin-top: 20px;
                display: inline-block;
                padding: 12px 22px;
                background: rgba(255, 255, 255, 0.45);
                backdrop-filter: blur(6px);
                color: #6d3b1a;
                border-radius: 22px;
                border: 1px solid rgba(255, 255, 255, 0.5);
                font-size: 2.1rem;
            }
            .welcome-personaje {
                margin-top: 22px;
                max-height: 380px;
                width: auto;
                filter: drop-shadow(0 14px 22px rgba(0, 0, 0, 0.3));
            }
            .stButton > button {
                background: linear-gradient(135deg, #b5e07d, #8bc34a) !important;
                font-size: 6rem !important;
                padding: 26px 0 !important;
                border-radius: 999px !important;
                width: 100% !important;
                margin-top: -30px !important;
                animation: flotar 3.6s ease-in-out infinite;
                box-shadow: 0 12px 30px rgba(139, 195, 74, 0.5) !important;
            }
            .stButton > button:hover {
                box-shadow: 0 14px 34px rgba(139, 195, 74, 0.65) !important;
            }
        </style>
        <div class='welcome-wrap'>
            <div class='welcome-floating'>
                <div class='welcome-title'>Bienvenido a Holi</div>
                <div class='welcome-subtitle'>Sistema de Predicción de Demanda</div>
                <div class='welcome-note'>Análisis inteligente, cálido y detallado para tu negocio.</div>
            </div>
        """
        + (f"<img class='welcome-personaje' src='data:image/png;base64,{personaje_base64}' />" if personaje_base64 else "")
        + """
        </div>
        """,
        unsafe_allow_html=True,
    )
    _, col_boton, _ = st.columns([2, 1.4, 2])
    with col_boton:
        if st.button("Comenzar", use_container_width=True):
            st.session_state.iniciado = True
            st.rerun()
    st.stop()


# ================================================================
# TÍTULO PRINCIPAL
# ================================================================
st.markdown(
    """
    <div class='hero-card'>
      <div class='hero-title'>Sistema de Predicción de Demanda</div>
      <div class='hero-subtitle'>Supermercados Holi</div>
      <div class='hero-note'>Análisis inteligente, cálido y detallado para tu negocio.</div>
    </div>
    """,
    unsafe_allow_html=True,
)
st.markdown("##### Análisis Inteligente basado en Big Data - Lima 2025")
st.markdown("---")


# ================================================================
# SIDEBAR - PANEL DE CONTROL
# ================================================================
st.sidebar.markdown("<div class='sidebar-title'>Panel de Control</div>", unsafe_allow_html=True)

st.sidebar.markdown("""
**Proyecto Big Data - VIII Ciclo**
Ingeniería de Sistemas

**Beneficiario:** Supermercados Holi
**Período:** Año 2025
""")

st.sidebar.markdown("---")


# ================================================================
# CARGA DE ARCHIVO
# ================================================================
st.subheader("Paso 1: Cargar el archivo de ventas")

archivo = st.file_uploader(
    "Selecciona el archivo Excel con los datos de ventas",
    type=["xlsx", "xls"],
    help="El archivo será procesado automáticamente con ETL",
)

if archivo is None:
    st.info("Sube un archivo Excel para comenzar el análisis")
    st.markdown("""
    ### ¿Qué hace este sistema?

    1. Carga un dataset de ventas con datos desordenados, duplicados, entre otros.
    2. Aplica ETL automáticamente (limpia duplicados, nulos, errores tipográficos)
    3. Genera un dashboard con KPIs y visualizaciones
    4. Predice la demanda futura con Machine Learning (Prophet)
    5. Genera reportes PDF ejecutivos descargables
    """)
    st.stop()


# ================================================================
# LECTURA DEL EXCEL
# ================================================================
try:
    df_original = pd.read_excel(archivo, engine="openpyxl")
except Exception as e:
    st.error(f"Error al leer el archivo: {e}")
    st.stop()

# Validar estructura
es_valido, faltantes = validar_columnas(df_original)
if not es_valido:
    st.error(f"Faltan columnas requeridas: {', '.join(faltantes)}")
    st.stop()

st.success(f"Archivo cargado correctamente — {len(df_original):,} registros encontrados")


# ================================================================
# PROCESO ETL (AUTOMÁTICO CON RESUMEN VISUAL)
# ================================================================
st.markdown("---")
st.subheader("Paso 2: Proceso ETL (Limpieza y Transformación)")

# Diagnóstico inicial
diagnostico = diagnosticar_dataset(df_original)

# Mostrar problemas detectados
with st.expander("Ver diagnóstico del dataset original (datos sucios)", expanded=True):
    col_d1, col_d2, col_d3, col_d4 = st.columns(4)
    with col_d1:
        st.metric("Registros totales", f"{diagnostico['total_registros']:,}")
    with col_d2:
        st.metric("Duplicados", diagnostico["duplicados"])
    with col_d3:
        st.metric("Valores nulos", diagnostico["total_nulos"])
    with col_d4:
        st.metric("Categorías detectadas", diagnostico.get("categorias_unicas_sucias", 0))

    st.markdown("**Distribución de valores nulos por columna:**")
    nulos_df = pd.DataFrame(
        list(diagnostico["nulos_por_columna"].items()),
        columns=["Columna", "Nulos"],
    )
    nulos_df = nulos_df[nulos_df["Nulos"] > 0]
    if len(nulos_df) > 0:
        st.dataframe(nulos_df, use_container_width=True, hide_index=True)
    else:
        st.success("Sin valores nulos detectados")

# Aplicar ETL
with st.spinner("⚙️ Aplicando proceso ETL..."):
    df, log = aplicar_etl(df_original)

# Resumen del ETL
st.markdown("### Resumen del Proceso ETL")

col_e1, col_e2, col_e3, col_e4 = st.columns(4)
with col_e1:
    st.metric(
        "Registros iniciales",
        f"{log['registros_iniciales']:,}",
    )
with col_e2:
    st.metric(
        "Registros finales",
        f"{log['registros_finales']:,}",
        delta=f"-{log['registros_eliminados']}",
        delta_color="inverse",
    )
with col_e3:
    st.metric(
        "Duplicados eliminados",
        log["duplicados_eliminados"],
    )
with col_e4:
    porcentaje = round(log["registros_finales"] / log["registros_iniciales"] * 100, 1)
    st.metric(
        "Calidad final",
        f"{porcentaje}%",
    )

# Detalles del ETL
with st.expander("Ver detalles del proceso ETL aplicado"):
    detalles = pd.DataFrame([
        {"Acción": "Duplicados eliminados", "Cantidad": log["duplicados_eliminados"]},
        {"Acción": "Fechas inválidas eliminadas", "Cantidad": log["fechas_invalidas_eliminadas"]},
        {"Acción": "Categorías normalizadas", "Cantidad": log["categorias_normalizadas"]},
        {"Acción": "Sucursales normalizadas", "Cantidad": log["sucursales_normalizadas"]},
        {"Acción": "Métodos de pago normalizados", "Cantidad": log["metodos_pago_normalizados"]},
        {"Acción": "Precios imputados (mediana)", "Cantidad": log["nulos_precio_imputados"]},
        {"Acción": "Stock imputado", "Cantidad": log["nulos_stock_imputados"]},
        {"Acción": "Método de pago imputado", "Cantidad": log["nulos_metodo_pago_imputados"]},
        {"Acción": "Cantidades inválidas eliminadas", "Cantidad": log["cantidades_invalidas_eliminadas"]},
        {"Acción": "Stock negativo corregido", "Cantidad": log["stock_negativo_corregido"]},
    ])
    st.dataframe(detalles, use_container_width=True, hide_index=True)

# Descarga del dataset limpio
buffer_excel = pd.ExcelWriter("dataset_limpio.xlsx", engine="openpyxl")
df.to_excel(buffer_excel, index=False, sheet_name="Ventas Limpio")
buffer_excel.close()

with open("dataset_limpio.xlsx", "rb") as f:
    st.download_button(
        label="⬇️ Descargar dataset LIMPIO (xlsx)",
        data=f,
        file_name="VENTAS_HOLI_2025_LIMPIO.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    )

st.success(f"ETL completado — Dataset limpio listo con {len(df):,} registros")


# ================================================================
# DASHBOARD PRINCIPAL
# ================================================================
st.markdown("---")
st.subheader("Paso 3: Dashboard Analítico")

# Calcular KPIs
kpis = calcular_kpis(df)

# Mostrar KPIs principales
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.markdown(f"""
    <div class='tarjeta-kpi'>
        <div class='kpi-etiqueta'>Ventas Totales</div>
        <div class='kpi-valor'>S/ {kpis['ventas_totales']:,.0f}</div>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown(f"""
    <div class='tarjeta-kpi'>
        <div class='kpi-etiqueta'>Productos Únicos</div>
        <div class='kpi-valor'>{kpis['productos_unicos']}</div>
    </div>
    """, unsafe_allow_html=True)

with col3:
    st.markdown(f"""
    <div class='tarjeta-kpi'>
        <div class='kpi-etiqueta'>Transacciones</div>
        <div class='kpi-valor'>{kpis['transacciones']:,}</div>
    </div>
    """, unsafe_allow_html=True)

with col4:
    st.markdown(f"""
    <div class='tarjeta-kpi'>
        <div class='kpi-etiqueta'>Ticket Promedio</div>
        <div class='kpi-valor'>S/ {kpis['ticket_promedio']:,.2f}</div>
    </div>
    """, unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)


# ================================================================
# MENÚ DE NAVEGACIÓN
# ================================================================
menu = st.sidebar.radio(
    "Sección:",
    ["Vista General", "Rankings", "Análisis ABC", "Rotación", "Predicción", "Reportes"],
)


# ================================================================
# SECCIÓN: VISTA GENERAL
# ================================================================
if menu == "Vista General":
    st.markdown("### Evolución y Distribución de Ventas")

    tab1, tab2, tab3 = st.tabs(["Evolución Temporal", "Por Sucursal", "Métodos de Pago"])

    with tab1:
        col1, col2 = st.columns(2)
        with col1:
            ventas_mensuales = analisis_temporal(df, "mensual")
            fig = px.line(
                ventas_mensuales,
                x="Periodo", y="Ventas",
                title="Evolución Mensual de Ventas",
                markers=True,
            )
            fig.update_traces(line_color="#667eea", line_width=3)
            st.plotly_chart(fig, use_container_width=True)

        with col2:
            ventas_diarias = analisis_temporal(df, "diaria")
            fig = px.area(
                ventas_diarias,
                x="Periodo", y="Ventas",
                title="Tendencia Diaria",
            )
            fig.update_traces(line_color="#764ba2")
            st.plotly_chart(fig, use_container_width=True)

    with tab2:
        col1, col2 = st.columns(2)
        with col1:
            ventas_suc = ventas_por_sucursal(df)
            fig = px.bar(
                ventas_suc,
                x="SUCURSAL", y="Ventas_Totales",
                title="Ventas por Sucursal",
                color="Ventas_Totales",
                color_continuous_scale=["#FFCC99", "#FF9E0F", "#5E2638"],
            )
            st.plotly_chart(fig, use_container_width=True)

        with col2:
            fig = px.pie(
                ventas_suc,
                names="SUCURSAL", values="Ventas_Totales",
                title="Distribución porcentual",
                hole=0.4,
            )
            st.plotly_chart(fig, use_container_width=True)

        st.dataframe(ventas_suc, use_container_width=True, hide_index=True)

    with tab3:
        col1, col2 = st.columns(2)
        metodo_pago = ventas_por_metodo_pago(df)

        with col1:
            fig = px.bar(
                metodo_pago,
                x="METODO_PAGO", y="Ventas_Totales",
                title="Ventas por Método de Pago",
                color="METODO_PAGO",
                color_discrete_sequence=["#FF9E0F", "#FFCC99", "#5E2638"],
            )
            st.plotly_chart(fig, use_container_width=True)

        with col2:
            fig = px.pie(
                metodo_pago,
                names="METODO_PAGO", values="Transacciones",
                title="Transacciones por Método",
                hole=0.4,
            )
            st.plotly_chart(fig, use_container_width=True)


# ================================================================
# SECCIÓN: RANKINGS
# ================================================================
elif menu == "Rankings":
    st.markdown("### Rankings de Productos y Categorías")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("#### Top 10 Productos")
        top = top_productos(df, n=10)
        fig = px.bar(
            top,
            x="TOTAL_VENTA", y="PRODUCTO",
            orientation="h",
            color="TOTAL_VENTA",
            color_continuous_scale=["#FFCC99", "#FF9E0F", "#5E2638"],
        )
        fig.update_layout(yaxis={"categoryorder": "total ascending"})
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        st.markdown("#### Ventas por Categoría")
        cat = ventas_por_categoria(df)
        fig = px.bar(
            cat,
            x="CATEGORIA", y="Ventas_Totales",
            color="CATEGORIA",
        )
        st.plotly_chart(fig, use_container_width=True)

    st.markdown("#### Tabla Completa - Top Productos")
    st.dataframe(top, use_container_width=True, hide_index=True)


# ================================================================
# SECCIÓN: ANÁLISIS ABC
# ================================================================
elif menu == "Análisis ABC":
    st.markdown("### Clasificación ABC de Productos")
    st.markdown("""
    El análisis ABC clasifica los productos según el **principio de Pareto (80/20)**:
    - **Categoría A**: productos que generan el 80% de las ventas
    - **Categoría B**: productos que aportan el 15%
    - **Categoría C**: productos de baja rotación (5%)
    """)

    abc = analisis_abc(df)
    resumen = resumen_abc(abc)

    col1, col2, col3 = st.columns(3)
    with col1:
        cat_a = resumen[resumen["Clasificación"] == "A"]
        if not cat_a.empty:
            st.metric("Categoría A", f"{int(cat_a['Productos'].iloc[0])} productos",
                     f"{cat_a['Porcentaje'].iloc[0]:.1f}% ventas")
    with col2:
        cat_b = resumen[resumen["Clasificación"] == "B"]
        if not cat_b.empty:
            st.metric("Categoría B", f"{int(cat_b['Productos'].iloc[0])} productos",
                     f"{cat_b['Porcentaje'].iloc[0]:.1f}% ventas")
    with col3:
        cat_c = resumen[resumen["Clasificación"] == "C"]
        if not cat_c.empty:
            st.metric("Categoría C", f"{int(cat_c['Productos'].iloc[0])} productos",
                     f"{cat_c['Porcentaje'].iloc[0]:.1f}% ventas")

    fig = px.bar(
        abc.head(30),
        x="PRODUCTO", y="TOTAL_VENTA",
        color="Clasificación",
        title="Top 30 Productos con Clasificación ABC",
        color_discrete_map={"A": "#5E2638", "B": "#FF9E0F", "C": "#FFCC99"},
    )
    fig.update_xaxes(tickangle=-45)
    st.plotly_chart(fig, use_container_width=True)

    st.markdown("#### Tabla Completa")
    st.dataframe(abc, use_container_width=True, hide_index=True)


# ================================================================
# SECCIÓN: ROTACIÓN
# ================================================================
elif menu == "Rotación":
    st.markdown("### Análisis de Rotación de Productos")
    st.markdown("La rotación diaria indica cuántas unidades se venden por día de cada producto.")

    rotacion = analisis_rotacion(df)

    fig = px.scatter(
        rotacion.head(30),
        x="Rotación_Diaria", y="Ventas_Totales",
        size="Unidades_Vendidas",
        hover_data=["PRODUCTO"],
        title="Rotación vs Ventas (Top 30)",
        color="Ventas_Totales",
        color_continuous_scale=["#FFCC99", "#FF9E0F", "#5E2638"],
    )
    st.plotly_chart(fig, use_container_width=True)

    st.markdown("#### Tabla de Rotación")
    st.dataframe(rotacion, use_container_width=True, hide_index=True)


# ================================================================
# SECCIÓN: PREDICCIÓN
# ================================================================
elif menu == "Predicción":
    st.markdown("### Predicción de Demanda con Machine Learning (Prophet)")

    if not PROPHET_DISPONIBLE:
        st.warning("La librería **Prophet** no está instalada todavía. Para instalarla ejecuta en la terminal:")
        st.code("pip install prophet", language="bash")
        if st.button("Verificar de nuevo / Recargar app"):
            st.rerun()
    else:
        productos_lista = ["Todos los productos"] + sorted(df["PRODUCTO"].unique().tolist())

        with st.form("prediccion_form"):
            col1, col2 = st.columns([2, 1])

            with col1:
                producto_sel = st.selectbox("Producto", productos_lista)
                dias = st.slider("Días a predecir", 7, 90, 30)
                agrupacion = st.selectbox("Agrupación", ["diaria", "semanal", "mensual"])

            with col2:
                st.info("Prophet predice la demanda futura basándose en patrones históricos.")
                ejecutar = st.form_submit_button("Generar Predicción")

        if ejecutar:
            with st.spinner("Entrenando modelo Prophet..."):
                serie, forecast, error = predecir_demanda(df, producto_sel, dias, agrupacion)

            if error:
                st.error(error)
            else:
                fig = go.Figure()
                fig.add_trace(go.Scatter(
                    x=serie["ds"], y=serie["y"],
                    mode="lines+markers",
                    name="Ventas Reales",
                    line=dict(color="#FF9E0F", width=2),
                ))
                fig.add_trace(go.Scatter(
                    x=forecast["ds"], y=forecast["yhat"],
                    mode="lines",
                    name="Predicción",
                    line=dict(color="#D35400", width=3, dash="dash"),
                ))
                fig.add_trace(go.Scatter(
                    x=forecast["ds"], y=forecast["yhat_upper"],
                    mode="lines", line=dict(width=0),
                    showlegend=False,
                ))
                fig.add_trace(go.Scatter(
                    x=forecast["ds"], y=forecast["yhat_lower"],
                    mode="lines", line=dict(width=0),
                    fill="tonexty",
                    fillcolor="rgba(211, 84, 0, 0.15)",
                    name="Intervalo de confianza",
                ))
                fig.update_layout(
                    title=f"Predicción de demanda: {producto_sel}",
                    xaxis_title="Fecha",
                    yaxis_title="Cantidad",
                    height=520,
                    hovermode="x unified",
                )
                st.plotly_chart(fig, use_container_width=True)

                resumen = resumen_prediccion(serie, forecast, dias)
                if resumen:
                    st.markdown("### Resumen de la Predicción")
                    c1, c2, c3, c4 = st.columns(4)
                    c1.metric("Demanda total predicha", f"{resumen['demanda_total_predicha']:,} und")
                    c2.metric("Promedio diario", f"{resumen['demanda_promedio_diaria']}")
                    c3.metric("Máximo esperado", f"{resumen['demanda_maxima']}")
                    c4.metric("Variación vs histórico", f"{resumen['variacion_vs_historico']}%")

                futuro = obtener_prediccion_futura(serie, forecast)
                if futuro is not None:
                    st.markdown("### Predicción detallada")
                    st.dataframe(futuro, use_container_width=True, hide_index=True)
        else:
            st.info("Selecciona opciones y presiona 'Generar Predicción' para ver los resultados.")


# ================================================================
# SECCIÓN: REPORTES
# ================================================================
elif menu == "Reportes":
    st.markdown("### Generación de Reporte Ejecutivo")
    st.markdown("Descarga un PDF profesional con todo el análisis del negocio.")

    abc_data = analisis_abc(df)
    resumen_abc_data = resumen_abc(abc_data)
    top_data = top_productos(df, n=10)

    col1, col2 = st.columns(2)
    with col1:
        st.markdown("#### Contenido del reporte:")
        st.markdown("""
        - Indicadores clave del negocio (KPIs)
        - Top 10 productos más vendidos
        - Clasificación ABC detallada
        - Resumen del proceso ETL aplicado
        - Fecha de generación
        """)

    with col2:
        st.markdown("#### Acciones")
        if st.button("Generar PDF Ejecutivo", use_container_width=True):
            with st.spinner("Generando reporte PDF..."):
                buffer = generar_pdf_ejecutivo(kpis, top_data, resumen_abc_data, log_etl=log)

            st.success("Reporte generado correctamente")
            st.download_button(
                label="⬇️ Descargar Reporte PDF",
                data=buffer,
                file_name=f"Reporte_Holi_{pd.Timestamp.now().strftime('%Y%m%d_%H%M')}.pdf",
                mime="application/pdf",
                use_container_width=True,
            )


# ================================================================
# PIE DE PÁGINA
# ================================================================
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #666; padding: 20px;'>
    <p><strong>Sistema de Predicción de Demanda - Supermercados Holi</strong></p>
    <p>Proyecto Big Data - VIII Ciclo | Ingeniería de Sistemas | Lima, 2026</p>
</div>
""", unsafe_allow_html=True)
