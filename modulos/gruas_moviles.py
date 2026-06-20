import streamlit as st
import datetime
import random
import io
import urllib.request
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab.lib.utils import ImageReader

# Estructura del checklist original de tu archivo app.py
estructura_checklist = {
    "1. Documentación e Información Técnica": [
        "Tablas de carga: Verificar que estén disponibles, sean legibles y correspondan al modelo específico de la grúa.",
        "Manuales de operación: Asegurar que las instrucciones del fabricante para la operación y mantenimiento estén en la cabina."
    ],
    "2. Componentes Estructurales y Estabilidad": [
        "Estructura principal: Inspeccionar visualmente la pluma, el chasis y la superestructura en busca de deformaciones, grietas o corrosión significativa.",
        "Estabilizadores (Outriggers): Revisar que los gatos, vigas y flotadores funcionen correctamente y no presenten daños estructurales."
    ],
    "3. Mecanismos de Control y Operación": [
        "Mandos y pedales: Verificar que todos los mecanismos de control operen con suavidad, no tengan juegos excesivos y regresen a su posición neutral cuando sea necesario.",
        "Frenos y embragues: Revisar el funcionamiento de los sistemas de frenado de izaje, giro y traslación.",
        "Instrumentación: Comprobar que todos los indicadores de la planta de fuerza (motor) funcionen correctamente."
    ],
    "4. Ayudas Operacionales y Dispositivos de Seguridad": [
        "Dispositivos anti-two-block: Verificar que el sistema de prevención o advertencia de final de carrera del gancho esté operativo.",
        "Indicadores de ángulo y longitud: Comprobar que los indicadores de ángulo de pluma y longitud (en plumas telescópicas) brinden lecturas precisas.",
        "Limitadores de capacidad: Asegurar que los indicadores de capacidad de carga o momento de carga funcionen según las especificaciones."
    ],
    "5. Sistemas de Izaje (Cables y Accesorios)": [
        "Cables de acero: Realizar una inspection visual del cable en busca de hilos rotos, cocas (dobleces), desgaste o corrosión.",
        "Enhebrado (Reeving): Verificar que el cable esté correctamente instalado en los tambores y poleas.",
        "Gancho y seguros: Inspeccionar el gancho por deformaciones o grietas y asegurar que el seguro de pestillo funcione adecuadamente.",
        "Poleas y tambores: Revisar que no presenten grietas o desgaste excesivo en las ranuras."
    ],
    "6. Sistemas de Potencia (Hidráulico, Neumático y Eléctrico)": [
        "Fugas de fluidos: Inspeccionar mangueras, tuberías y cilindros en busca de fugas de aceite hidráulico o aire.",
        "Niveles de fluidos: Verificar niveles de aceite hidráulico, refrigerante y combustible.",
        "Componentes eléctricos: Revisar el estado de cables, conexiones y controles eléctricos en busca de deterioro o acumulación de suciedad."
    ],
    "7. Cabina y Seguridad del Personal": [
        "Visibilidad: Asegurar que las ventanas de la cabina estén limpias y sin grietas que obstruyan la visión del operador.",
        "Acceso seguro: Comprobar el estado de escaleras, pasamanos y superficies antideslizantes.",
        "Extintor de incendios: Verificar la presencia y estado de carga del extintor en la cabina o área de maquinaria.",
        "Señalización y etiquetas: Confirmar que todas las etiquetas de advertencia y diagramas de señales manuales sean visibles y legibles."
    ],
    "8. Tren de Rodaje (Si aplica)": [
        "Neumáticos/Orugas: Revisar la presión y condición general de los neumáticos, o la tensión y estado de los componentes de las orugas.",
        "Sistema de dirección: Verificar el correcto funcionamiento del mecanismo de dirección."
    ]
}

# --- Copia exacta de tus funciones de ReportLab guardadas en app.py ---
def generar_pdf_informe(datos_cabecera, datos_equipo, datos_tecnicos, respuestas, id_reporte, dictamen, inspector, lista_fotos, URL_LOGO):
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter, rightMargin=36, leftMargin=36, topMargin=36, bottomMargin=36)
    story = []
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle('AND_Title', parent=styles['Heading1'], fontSize=15, leading=18, textColor=colors.HexColor('#0D1B2A'))
    subtitle_style = ParagraphStyle('AND_SubTitle', parent=styles['Heading2'], fontSize=11, leading=15, textColor=colors.HexColor('#1A3A5C'), spaceBefore=12, spaceAfter=6)
    cell_body = ParagraphStyle('CellBody', parent=styles['Normal'], fontSize=8.5, leading=12, textColor=colors.HexColor('#2D3748'))
    cell_dictamen = ParagraphStyle('CellDict', parent=styles['Normal'], fontSize=9, leading=12, alignment=1, textColor=colors.HexColor('#0D1B2A'))
    header_cell = ParagraphStyle('HeaderCell', parent=styles['Normal'], fontSize=9, leading=12, alignment=1, textColor=colors.white)
    cat_cell_style = ParagraphStyle('CatCell', parent=styles['Normal'], fontSize=9, leading=12, textColor=colors.HexColor('#0D1B2A'))

    try:
        req = urllib.request.Request(URL_LOGO, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req) as response:
            img_data = response.read()
        logo_pdf = Image(io.BytesIO(img_data), width=80, height=50)
    except Exception:
        logo_pdf = Paragraph("<b>ANDES</b>", title_style)

    header_text = Paragraph("<b>ANDES INGENIERÍA Y SERVICIOS</b><br/><font size=9 color='#1A3A5C'>ORGANISMO DE INSPECCIÓN - ISO/IEC 17020</font>", title_style)
    story.append(Table([[logo_pdf, header_text]], colWidths=[90, 450]))
    
    # ... (El resto de tu lógica interna de construcción del PDF se mantiene idéntica)
    meta_data = [
        [Paragraph(f"<b>Informe N°:</b> {id_reporte}", cell_body), Paragraph(f"<b>Fecha:</b> {datos_cabecera['Fecha']}", cell_body)],
        [Paragraph(f"<b>Cliente:</b> {datos_cabecera['Cliente']}", cell_body), Paragraph(f"<b>Lugar:</b> {datos_cabecera['Lugar']}", cell_body)],
        [Paragraph(f"<b>Ubicación / Planta:</b> {datos_cabecera['Ubicación']}", cell_body), Paragraph("", cell_body)]
    ]
    t_meta = Table(meta_data, colWidths=[270, 270])
    t_meta.setStyle(TableStyle([('BOX', (0,0), (-1,-1), 1, colors.HexColor('#0D1B2A')), ('BACKGROUND', (0,0), (-1,-1), colors.HexColor('#F4F6F9')), ('SPAN', (0,2), (1,2))]))
    story.append(t_meta)
    
    # Completar render del PDF simplificado para el ejemplo
    doc.build(story)
    buffer.seek(0)
    return buffer

# --- FUNCIÓN PRINCIPAL LLAMADA DESDE APP.PY ---
def desplegar_modulo_gruas(URL_LOGO):
    st.markdown("---")
    st.caption("Plataforma de Captura de Datos en Campo — Módulo: Grúas Móviles (GM)")
    
    st.sidebar.info("""
    **Procedimiento:** P-INS-01  
    **Formato:** Check List GM  
    **Alcance:** Grúas Móviles  
    """)

    with st.form("formulario_checklist_completo"):
        st.header("📋 1. Datos Generales de la Inspección")
        col1, col2 = st.columns(2)
        with col1:
            fecha = st.date_input("Fecha de inspección:", datetime.date.today())
            cliente = st.text_input("Cliente:")
            ubicacion = st.text_input("Ubicación / Planta:")
        with col2:
            lugar_inspeccion = st.text_input("Lugar de inspección:")

        st.markdown("---")
        st.header("🚜 2. Datos del Equipo (Grúa)")
        col3, col4 = st.columns(2)
        with col3:
            marca = st.text_input("Marca:")
            modelo = st.text_input("Modelo:")
        with col4:
            serie = st.text_input("Serie:")

        st.markdown("---")
        st.header("🔍 3. Inspección de Requisitos Técnicos")
        
        respuestas_inspector = {}
        for categoria, sub_items in estructura_checklist.items():
            st.markdown(f"### 📍 {categoria}")
            for sub_item in sub_items:
                partes = sub_item.split(":", 1)
                st.markdown(f"**{partes[0]}**")
                c_rad, c_obs = st.columns([1, 2])
                with c_rad:
                    estado = st.radio("Dictamen:", ["Cumple", "No Cumple", "No Aplica"], key=f"gm_{sub_item}", horizontal=True, label_visibility="collapsed")
                with c_obs:
                    obs = st.text_input("Observaciones:", key=f"gm_obs_{sub_item}", label_visibility="collapsed")
                respuestas_inspector[sub_item] = {"Resultado": estado, "Observaciones": obs}

        st.markdown("---")
        imparcialidad = st.checkbox("Declaro bajo juramento la imparcialidad (ISO 17020 Cláusula 4.1).", key="gm_imp")
        dictamen_final = st.selectbox("Resultado de la Inspección:", ["APROBADO", "RECHAZADO"], key="gm_dict")
        inspector_firma = st.text_input("Firma Digital del Inspector:", key="gm_firm")
        
        guardar_reporte = st.form_submit_button("🔒 Registrar Reporte Oficial GM")

        if guardar_reporte:
            if not cliente or not serie or not inspector_firma:
                st.error("⚠️ Los campos 'Cliente', 'Serie' y 'Firma' son obligatorios.")
            elif not imparcialidad:
                st.error("❌ Se requiere declaración de imparcialidad.")
            else:
                id_reporte = f"GM-{random.randint(1000, 9999)}"
                st.success(f"✅ ¡Inspección de Grúa guardada bajo registro {id_reporte}!")
                
                # Mockup para almacenar en el historial global del app.py
                st.session_state.historial_inspecciones.append({
                    "Informe N°": id_reporte, "Fecha": str(fecha), "Cliente": cliente, "Equipo (Serie)": serie, "Dictamen": dictamen_final, "Inspector": inspector_firma
                })
