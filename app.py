import streamlit as st
import os

# Configuración visual global de la plataforma (ANDES)
st.set_page_config(page_title="ANDES - Sistema de Gestión de Inspecciones", layout="wide")

URL_LOGO = "https://raw.githubusercontent.com/sklayerx/plataforma17020/main/logo_andes.png"

st.markdown("""
    <style>
    .stApp { background-color: #F4F6F9; }
    h1, h2, h3 { color: #0D1B2A !important; font-family: Arial, sans-serif; }
    div[data-testid="stForm"] { background-color: #FFFFFF; border: 1px solid #1A3A5C; border-radius: 8px; padding: 30px; }
    section[data-testid="stSidebar"] { background-color: #0D1B2A; }
    section[data-testid="stSidebar"] h1, section[data-testid="stSidebar"] h2, section[data-testid="stSidebar"] p { color: #FFFFFF !important; }
    </style>
""", unsafe_allow_html=True)

# --- ENCABEZADO UNIFICADO DE LA PLATAFORMA ---
col_logo, col_titulo = st.columns([1, 4])
with col_logo:
    try:
        st.image(URL_LOGO, width=140)
    except:
        st.markdown("<h2 style='color:#0D1B2A; margin:0;'>🏔️ ANDES</h2>", unsafe_allow_html=True) 
with col_titulo:
    st.title("ANDES — Ingeniería y Servicios")
    st.subheader("Sistema de Gestión de Inspecciones Oficiales (ISO/IEC 17020)")

# Inicializar historiales globales en session_state si no existen
if 'historial_inspecciones' not in st.session_state:
    st.session_state.historial_inspecciones = []

# --- PANEL LATERAL DE NAVEGACIÓN ---
st.sidebar.markdown("<h2 style='color:#FFFFFF;'>ANDES</h2>", unsafe_allow_html=True)
st.sidebar.markdown("<p style='color:#F4F6F9; font-size:12px;'>Elevación, precisión y crecimiento</p>", unsafe_allow_html=True)
st.sidebar.markdown("---")

st.sidebar.header("🚜 Listado de Equipos")
# Selector principal para desplegar la plataforma correspondiente
modulo_seleccionado = st.sidebar.selectbox(
    "Seleccione el equipo a inspeccionar:",
    [
        "Seleccione un equipo...",
        "Grúas Móviles (Módulo GM)",
        "Grilletes (Módulo GR)",
        "Eslingas Sintéticas (Módulo ES)"
    ]
)

# --- CARGA DINÁMICA DE MÓDULOS ---
if modulo_seleccionado == "Seleccione un equipo...":
    st.markdown("---")
    st.info("👋 **Bienvenido al sistema de captura en campo de ANDES.** Por favor, seleccione un tipo de equipo en el listado del panel izquierdo para desplegar su respectiva plataforma de carga.")
    
elif modulo_seleccionado == "Grúas Móviles (Módulo GM)":
    from modulos.gruas_moviles import desplegar_modulo_gruas
    desplegar_modulo_gruas(URL_LOGO)

elif modulo_seleccionado == "Grúas de Pluma Articulada (Módulo GPA)":
    from modulos.pluma_articulada import desplegar_modulo_pluma_articulada
    desplegar_modulo_pluma_articulada(URL_LOGO)

elif modulo_seleccionado == "Eslingas Sintéticas (Módulo ES)":
    st.markdown("---")
    st.caption("Plataforma de Captura de Datos en Campo — Módulo: Eslingas (ES)")
    st.warning("🏗️ El módulo de Eslingas (ASME B30.9) está listo para integrar su lógica específica.")
