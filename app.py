import streamlit as st
import datetime
import random

# Configuración de la página
st.set_page_config(page_title="Sistema de Inspección - ISO 17020", layout="wide")

st.title("🛡️ Sistema de Gestión de Inspecciones (ISO/IEC 17020)")
st.caption("Plataforma Digital de Captura de Datos en Campo — Check List General")

# Inicializar base de datos en sesión
if 'historial_inspecciones' not in st.session_state:
    st.session_state.historial_inspecciones = []

# --- PANEL LATERAL ---
st.sidebar.header("⚙️ Control de Operaciones")
st.sidebar.info("""
**Procedimiento:** P-INS-01  
**Formato:** Check List GM  
**Versión del Formulario:** 2.0  
""")

# --- SECCIÓN 1: DATOS DE CABECERA (Trazabilidad Requisito 7.4) ---
st.header("📋 Datos Generales de la Inspección")

with st.form("formulario_checklist"):
    col1, col2 = st.columns(2)
    with col1:
        inspector = st.text_input("Nombre del Inspector Autorizado:")
        cliente = st.text_input("Cliente / Empresa:")
        ubicacion = st.text_input("Ubicación / Planta / Instalación:")
    with col2:
        fecha = st.date_input("Fecha de Evaluación:", datetime.date.today())
        equipo_id = st.text_input("Identificación del Equipo / Ítem Inspeccionado (ID/Tag):")

    st.markdown("---")
    
    # --- SECCIÓN 2: DECLARACIÓN JURADA DE IMPARCIALIDAD (Requisito 4.1) ---
    st.subheader("⚖️ Control de Imparcialidad e Independencia")
    imparcialidad = st.checkbox("Declaro formalmente que no poseo conflictos de interés comerciales, financieros ni técnicos respecto al ítem evaluado.")

    st.markdown("---")

    # --- SECCIÓN 3: EL CHECK LIST DE TU EXCEL/DOCX ---
    st.header("📊 Evaluación de Requisitos Técnicos")
    st.info("Seleccione la calificación para cada punto evaluado y agregue observaciones de ser necesario.")

    # Definimos los ítems de tu documento
    items_evaluacion = [
        "1. Estado General de Estructuras y Soportes",
        "2. Condiciones de Seguridad del Entorno de Trabajo",
        "3. Integridad de Conexiones Fisicoquímicas y Mecánicas",
        "4. Hermeticidad / Ausencia de Fugas Visibles",
        "5. Estado de Sistemas de Control / Tableros / Instrumentación",
        "6. Cumplimiento de Señalización de Seguridad y Rotulado",
        "7. Orden, Limpieza y Mantenimiento General del Área"
    ]

    # Diccionario para almacenar las respuestas del inspector
    respuestas = {}
    
    for item in items_evaluacion:
        st.markdown(f"##### {item}")
        c1, c2 = st.columns([1, 2])
        with c1:
            # Calificación estandarizada para auditorías
            estado = st.radio(f"Resultado:", ["Cumple", "No Cumple", "No Aplica"], key=f"rad_{item}", horizontal=True)
        with c2:
            obs = st.text_input("Observaciones / Hallazgos específicos:", key=f"obs_{item}", placeholder="Escriba aquí los detalles si aplica...")
        
        # Guardamos el resultado de esta fila
        respuestas[item] = {"Resultado": estado, "Observaciones": obs}
        st.markdown("<br>", unsafe_allow_html=True)

    st.markdown("---")
    
    # --- SECCIÓN 4: DICTAMEN FINAL ---
    st.subheader("🏁 Conclusión de la Inspección")
    dictamen = st.selectbox("Dictamen Técnico Final:", ["APROBADO", "RECHAZADO", "APROBADO CONDICIONAL"])

    # Botón para procesar y firmar digitalmente el formulario
    enviar_checklist = st.form_submit_button("🔒 Firmar y Registrar Reporte Técnico")

    if enviar_checklist:
        if not inspector or not cliente or not equipo_id:
            st.error("⚠️ Error de Integridad: Los campos de Inspector, Cliente e Identificación del Equipo son obligatorios.")
        elif not imparcialidad:
            st.error("❌ Bloqueo ISO 17020: Es obligatorio aceptar la declaración de imparcialidad antes de emitir un juicio técnico.")
        else:
            # Generar código único correlativo
            codigo_informe = f"REP-{fecha.strftime('%Y%m%d')}-{random.randint(1000, 9999)}"
            
            # Estructurar registro final
            registro = {
                "Código Reporte": codigo_informe,
                "Fecha": str(fecha),
                "Inspector": inspector,
                "Cliente": cliente,
                "ID Equipo": equipo_id,
                "Dictamen Final": dictamen
            }
            
            # Guardamos en la base de datos de la sesión
            st.session_state.historial_inspecciones.append(registro)
            st.success(f"🎉 ¡Check List procesado con éxito! Código de registro asignado: **{codigo_informe}**")

# --- SECCIÓN 5: HISTORIAL Y REGISTROS INALTERABLES (Requisito 8.4) ---
st.markdown("---")
st.header("🗄️ Historial de Reportes Emitidos")

if st.session_state.historial_inspecciones:
    st.dataframe(st.session_state.historial_inspecciones, use_container_width=True)
else:
    st.warning("No se han registrado reportes en este ciclo de trabajo.")
