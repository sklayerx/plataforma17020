import streamlit as st
import datetime
import random
import io
import urllib.request
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors

# ==========================================
# CONFIGURACIÓN VISUAL DE LA PLATAFORMA (ANDES)
# ==========================================
st.set_page_config(page_title="ANDES - Inspección de Grúas Móviles", layout="wide")

# URL Directa de la imagen del logo en GitHub
URL_LOGO = "https://raw.githubusercontent.com/tu-usuario/plataforma17020/main/logo_andes.png"

st.markdown("""
    <style>
    .stApp { background-color: #F4F6F9; }
    h1, h2, h3 { color: #0D1B2A !important; font-family: Arial, sans-serif; }
    div[data-testid="stForm"] { background-color: #FFFFFF; border: 1px solid #1A3A5C; border-radius: 8px; padding: 30px; }
    section[data-testid="stSidebar"] { background-color: #0D1B2A; }
    section[data-testid="stSidebar"] h1, section[data-testid="stSidebar"] h2, section[data-testid="stSidebar"] p { color: #FFFFFF !important; }
    </style>
""", unsafe_allow_html=True)

# --- ENCABEZADO DE LA PLATAFORMA CON LOGO ---
col_logo, col_titulo = st.columns([1, 4])
with col_logo:
    try:
        st.image(URL_LOGO, width=140)
    except:
        st.markdown("<h2 style='color:#0D1B2A; margin:0;'>🏔️ ANDES</h2>", unsafe_allow_html=True) 
with col_titulo:
    st.title("ANDES — Ingeniería y Servicios")
    st.subheader("Sistema de Gestión de Inspecciones Oficiales (ISO/IEC 17020)")
    st.caption("Plataforma de Captura de Datos en Campo — Módulo: Grúas Móviles (GM)")

# Inicializar base de datos en sesión
if 'historial_inspecciones' not in st.session_state:
    st.session_state.historial_inspecciones = []

# --- PANEL LATERAL INSTITUCIONAL ---
st.sidebar.markdown("<h2 style='color:#FFFFFF;'>ANDES</h2>", unsafe_allow_html=True)
st.sidebar.markdown("<p style='color:#F4F6F9; font-size:12px;'>Elevación, precisión y crecimiento</p>", unsafe_allow_html=True)
st.sidebar.markdown("---")
st.sidebar.header("⚙️ Control de Operaciones")
st.sidebar.info("""
**Procedimiento:** P-INS-01  
**Formato:** Check List GM  
**Alcance:** Grúas Móviles  
**Estado:** Cumplimiento ISO 17020  
""")

# --- FUNCIONES PARA GENERACIÓN DE PDF CON LOGOTIPO CORREGIDO ---
def generar_pdf_informe(datos_cabecera, datos_equipo, datos_tecnicos, respuestas, id_reporte, dictamen, inspector):
    buffer = io.BytesIO()
    # Margen optimizado de 36 puntos (0.5 pulgadas) para ganar espacio de impresión
    doc = SimpleDocTemplate(buffer, pagesize=letter, rightMargin=36, leftMargin=36, topMargin=36, bottomMargin=36)
    story = []
    
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle('AND_Title', parent=styles['Heading1'], fontSize=15, leading=18, textColor=colors.HexColor('#0D1B2A'))
    subtitle_style = ParagraphStyle('AND_SubTitle', parent=styles['Heading2'], fontSize=11, leading=15, textColor=colors.HexColor('#1A3A5C'), spaceBefore=12, spaceAfter=6)
    
    # Nuevos estilos específicos para celdas dinámicas de tablas controladas
    cell_body = ParagraphStyle('CellBody', parent=styles['Normal'], fontSize=8.5, leading=11, textColor=colors.HexColor('#2D3748'))
    cell_dictamen = ParagraphStyle('CellDict', parent=styles['Normal'], fontSize=9, leading=11, alignment=1, textColor=colors.HexColor('#0D1B2A'))
    header_cell = ParagraphStyle('HeaderCell', parent=styles['Normal'], fontSize=9, leading=12, alignment=1, textColor=colors.white)
    
    # Descarga e Inyección del Logotipo
    try:
        req = urllib.request.Request(URL_LOGO, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req) as response:
            img_data = response.read()
        logo_pdf = Image(io.BytesIO(img_data), width=80, height=50)
    except Exception:
        # Ajuste de marca de respaldo robusto en caso de error de red
        logo_pdf = Paragraph("<b>ANDES</b><br/><font size=6 color='#1A3A5C'>INGENIERÍA</font>", ParagraphStyle('BackLogo', fontSize=14, leading=15, textColor=colors.HexColor('#0D1B2A')))

    header_text = Paragraph("""
        <b>ANDES INGENIERÍA Y SERVICIOS</b><br/>
        <font size=9 color='#1A3A5C'>ORGANISMO DE INSPECCIÓN ACREDITADO - ISO/IEC 17020</font><br/>
        <font size=10 color='#0D1B2A'>INFORME TÉCNICO DETALLADO DE INSPECCIÓN — GRÚAS MÓVILES</font>
    """, title_style)
    
    t_header = Table([[logo_pdf, header_text]], colWidths=[90, 450])
    t_header.setStyle(TableStyle([('VALIGN', (0,0), (-1,-1), 'MIDDLE'), ('BOTTOMPADDING', (0,0), (-1,-1), 10)]))
    story.append(t_header)
    story.append(Spacer(1, 5))
    
    # Tabla de metadatos del reporte
    meta_data = [
        [Paragraph(f"<b>Informe N°:</b> {id_reporte}", cell_body), Paragraph(f"<b>Fecha:</b> {datos_cabecera['Fecha']}", cell_body)],
        [Paragraph(f"<b>Cliente:</b> {datos_cabecera['Cliente']}", cell_body), Paragraph(f"<b>Lugar:</b> {datos_cabecera['Lugar']}", cell_body)],
        [Paragraph(f"<b>Ubicación / Planta:</b> {datos_cabecera['Ubicación']}", cell_body), ""]
    ]
    t_meta = Table(meta_data, colWidths=[270, 270])
    t_meta.setStyle(TableStyle([
        ('BOX', (0,0), (-1,-1), 1, colors.HexColor('#0D1B2A')),
        ('INNERGRID', (0,0), (-1,-1), 0.5, colors.HexColor('#1A3A5C')),
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor('#F4F6F9')),
        ('PADDING', (0,0), (-1,-1), 5),
        ('SPAN', (0,2), (1,2))
    ]))
    story.append(t_meta)
    
    # Datos del Equipo
    story.append(Paragraph("1. Identificación y Especificaciones Técnicas del Equipo", subtitle_style))
    equipo_data = [
        [Paragraph(f"<b>Marca:</b> {datos_equipo['Marca']}", cell_body), Paragraph(f"<b>Modelo:</b> {datos_equipo['Modelo']}", cell_body), Paragraph(f"<b>N° Serie:</b> {datos_equipo['Serie']}", cell_body)],
        [Paragraph(f"<b>Año Fab.:</b> {datos_equipo['Año']}", cell_body), Paragraph(f"<b>Interno:</b> {datos_equipo['Interno']}", cell_body), Paragraph(f"<b>Patente:</b> {datos_equipo['Patente']}", cell_body)],
        [Paragraph(f"<b>N° Chasis:</b> {datos_equipo['Chasis']}", cell_body), Paragraph(f"<b>Capacidad:</b> {datos_tecnicos['Capacidad']}", cell_body), Paragraph(f"<b>Radio Trab.:</b> {datos_tecnicos['Radio']}", cell_body)],
        [Paragraph(f"<b>Tipo Pluma:</b> {datos_tecnicos['Pluma']}", cell_body), Paragraph(f"<b>Tren Rodante:</b> {datos_tecnicos['Tren']}", cell_body), ""]
    ]
    t_eq = Table(equipo_data, colWidths=[180, 180, 180])
    t_eq.setStyle(TableStyle([
        ('BOX', (0,0), (-1,-1), 1, colors.HexColor('#1A3A5C')), 
        ('INNERGRID', (0,0), (-1,-1), 0.5, colors.HexColor('#F4F6F9')), 
        ('PADDING', (0,0), (-1,-1), 5),
        ('SPAN', (0,3), (1,3))
    ]))
    story.append(t_eq)
    
    # CORRECCIÓN DE LA TABLA DE CHECKLIST (Cero solapamiento y anchos calibrados)
    story.append(Paragraph("2. Evaluación Técnica y Hallazgos de Campo", subtitle_style))
    check_data = [[
        Paragraph("<b>Ítem / Componente Evaluado</b>", header_cell), 
        Paragraph("<b>Dictamen</b>", header_cell), 
        Paragraph("<b>Observaciones / Hallazgos</b>", header_cell)
    ]]
    
    for item, resp in respuestas.items():
        # Sanación de textos y formato limpio
        item_limpio = item.replace("<b>", "").replace("</b>", "")
        partes = item_limpio.split(":", 1)
        titulo_item = f"<b>{partes[0]}</b>"
        if len(partes) > 1:
            titulo_item += f": {partes[1]}"
            
        # Inyección obligatoria dentro de componentes Paragraph para forzar la celda dinámica autowrap
        check_data.append([
            Paragraph(titulo_item, cell_body), 
            Paragraph(resp['Resultado'], cell_dictamen), 
            Paragraph(resp['Observaciones'] if resp['Observaciones'] else "Sin novedades registradas", cell_body)
        ])
        
    # Ancho exacto recalculado para hoja Letter (540 puntos totales de área imprimible)
    t_check = Table(check_data, colWidths=[210, 70, 260])
    t_check.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#0D1B2A')),
        ('ALIGN', (0,0), (-1,0), 'CENTER'),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#1A3A5C')),
        ('VALIGN', (0,0), (-1,-1), 'TOP'), # Alineación superior para evitar cortes feos
        ('TOPPADDING', (0,0), (-1,-1), 6),
        ('BOTTOMPADDING', (0,0), (-1,-1), 6),
        ('LEFTPADDING', (0,0), (-1,-1), 5),
        ('RIGHTPADDING', (0,0), (-1,-1), 5)
    ]))
    story.append(t_check)
    
    # Conclusión e Imparcialidad
    story.append(Paragraph("3. Conclusión de la Inspección y Firmas", subtitle_style))
    concl_data = [
        [Paragraph(f"<b>DICTAMEN TÉCNICO FINAL:</b> {dictamen}", ParagraphStyle('FinalD', parent=cell_body, fontSize=10))],
        [Paragraph(f"<b>Inspector Técnico Autorizado:</b> {inspector}", ParagraphStyle('FinalI', parent=cell_body, fontSize=9))],
        [Paragraph("<i>Este documento confidencial es emitido por ANDES Ingeniería y Servicios bajo las directrices de la norma ISO/IEC 17020.</i>", ParagraphStyle('FinalN', parent=cell_body, fontSize=7.5))]
    ]
    t_concl = Table(concl_data, colWidths=[540])
    t_concl.setStyle(TableStyle([
        ('BOX', (0,0), (-1,-1), 1.5, colors.HexColor('#0D1B2A')), 
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#F4F6F9')), 
        ('PADDING', (0,0), (-1,-1), 6)
    ]))
    story.append(t_concl)
    
    doc.build(story)
    buffer.seek(0)
    return buffer

def generar_pdf_certificado(datos_cabecera, datos_equipo, id_reporte, dictamen, inspector):
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter, rightMargin=50, leftMargin=50, topMargin=50, bottomMargin=50)
    story = []
    
    styles = getSampleStyleSheet()
    cert_title = ParagraphStyle('AND_CertTitle', parent=styles['Heading1'], fontSize=22, leading=26, alignment=1, textColor=colors.HexColor('#0D1B2A'), spaceAfter=25)
    cert_body = ParagraphStyle('AND_CertBody', parent=styles['BodyText'], fontSize=11, leading=20, alignment=4, spaceBefore=15)
    
    try:
        req = urllib.request.Request(URL_LOGO, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req) as response:
            img_data = response.read()
        logo_cert = Image(io.BytesIO(img_data), width=100, height=62)
        logo_cert.hAlign = 'CENTER'
        story.append(logo_cert)
    except Exception:
        pass
        
    story.append(Spacer(1, 10))
    story.append(Paragraph("<b>ANDES INGENIERÍA Y SERVICIOS</b>", ParagraphStyle('Brand', alignment=1, fontSize=12, textColor=colors.HexColor('#1A3A5C'))))
    story.append(Spacer(1, 10))
    story.append(Paragraph("<b>CERTIFICADO DE INSPECCIÓN Y APROBACIÓN</b>", cert_title))
    story.append(Paragraph(f"<b>Certificado Correlativo N°:</b> CERT-ANDES-{id_reporte}", ParagraphStyle('Sub', alignment=1, fontSize=11, textColor=colors.HexColor('#1A3A5C'))))
    story.append(Spacer(1, 20))
    
    texto = f"El <b>Organismo de Inspección de ANDES Ingeniería y Servicios</b>, conforme con los esquemas de evaluación normativos correspondientes, certifica que se ha ejecutado el protocolo de inspección de seguridad física y estructural sobre el siguiente ítem:"
    story.append(Paragraph(texto, cert_body))
    story.append(Spacer(1, 15))
    
    eq_info = [
        ["<b>Propietario / Cliente:</b>", datos_cabecera['Cliente']],
        ["<b>Categoría de Equipo:</b>", "Grúa Móvil (Módulo GM)"],
        ["<b>Marca / Modelo:</b>", f"{datos_equipo['Marca']} / {datos_equipo['Modelo']}"],
        ["<b>Número de Serie / Chasis:</b>", f"{datos_equipo['Serie']} / {datos_equipo['Chasis']}"],
        ["<b>Identificación Interna / Dominio:</b>", f"{datos_equipo['Interno']} / {datos_equipo['Patente']}"]
    ]
    t_eq = Table(eq_info, colWidths=[200, 270])
    t_eq.setStyle(TableStyle([
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#1A3A5C')), ('PADDING', (0,0), (-1,-1), 8),
        ('BACKGROUND', (0,0), (0,-1), colors.HexColor('#F4F6F9')), ('BOX', (0,0), (-1,-1), 1.5, colors.HexColor('#0D1B2A'))
    ]))
    story.append(t_eq)
    
    story.append(Spacer(1, 20))
    texto_dictamen = f"Habiéndose completado satisfactoriamente los ensayos técnicos de campo y listas de control vigentes, el veredicto oficial del organismo para este ítem es: <font color='#38A169'><b>{dictamen}</b></font>."
    story.append(Paragraph(texto_dictamen, cert_body))
    
    texto_val = f"<b>Fecha de Emisión:</b> {datos_cabecera['Fecha']}<br/><b>Vigencia Técnica Sugerida:</b> 1 Año a partir de la fecha de emisión."
    story.append(Paragraph(texto_val, cert_body))
    
    story.append(Spacer(1, 40))
    story.append(Paragraph(f"_______________________________________<br/><b>{inspector}</b><br/>Inspector Técnico Autorizado<br/><b>ANDES Ingeniería y Servicios</b>", ParagraphStyle('Firma', alignment=1, fontSize=10, leading=14)))
    
    doc.build(story)
    buffer.seek(0)
    return buffer


with st.form("formulario_checklist_completo"):
    
    # === SECCIÓN 1: DATOS DE CABECERA ===
    st.header("📋 1. Datos Generales de la Inspección")
    col1, col2 = st.columns(2)
    with col1:
        fecha = st.date_input("Fecha de inspección:", datetime.date.today())
        cliente = st.text_input("Cliente:")
        ubicacion = st.text_input("Ubicación / Planta:")
    with col2:
        lugar_inspeccion = st.text_input("Lugar de inspección:")

    st.markdown("---")

    # === SECCIÓN 2: DATOS DEL EQUIPO ===
    st.header("🚜 2. Datos del Equipo")
    col3, col4 = st.columns(2)
    with col3:
        marca = st.text_input("Marca:")
        modelo = st.text_input("Modelo:")
        serie = st.text_input("Serie:")
        anio_fab = st.text_input("Año de fabricación:")
    with col4:
        interno = st.text_input("Interno:")
        patente = st.text_input("Patente / Dominio:")
        n_chasis = st.text_input("N° de chasis:")

    st.markdown("---")

    # === SECCIÓN 3: DATOS TÉCNICOS ===
    st.header("⚙️ 3. Datos Técnicos")
    col5, col6 = st.columns(2)
    with col5:
        capacidad_carga = st.text_input("Capacidad de carga:")
        radio_trabajo = st.text_input("Radio de trabajo:")
    with col6:
        tipo_pluma = st.text_input("Tipo de pluma:")
        tren_rodante = st.text_input("Tren rodante:")

    st.markdown("---")
    
    # === SECCIÓN 4: CONTROL DE IMPARCIALIDAD (REQUISITO 4.1) ===
    st.subheader("⚖️ Control de Imparcialidad e Independencia")
    imparcialidad = st.checkbox("Declaro formalmente bajo juramento que no poseo conflictos de interés comerciales, financieros ni técnicos respecto al ítem evaluado.")

    st.markdown("---")

    # === SECCIÓN 5: INSPECCIÓN TÉCNICA EN DETALLE ===
    st.header("🔍 4. Inspección de Requisitos Técnicos")
    st.info("Seleccione la calificación para cada sub-ítem y registre observaciones en caso de desvíos.")

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
            "Cables de acero: Realizar una inspección visual del cable en busca de hilos rotos, cocas (dobleces), desgaste o corrosión.",
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

    respuestas_inspector = {}

    for categoria, sub_items in estructura_checklist.items():
        st.markdown(f"### 📍 {categoria}")
        for sub_item in sub_items:
            partes = sub_item.split(":", 1)
            titulo_item = partes[0]
            descripcion_item = partes[1] if len(partes) > 1 else ""
            
            st.markdown(f"**{titulo_item}** — *{descripcion_item.strip()}*")
            c_rad, c_obs = st.columns([1, 2])
            with c_rad:
                estado = st.radio("Dictamen:", ["Cumple", "No Cumple", "No Aplica"], key=f"rad_{sub_item}", horizontal=True, label_visibility="collapsed")
            with c_obs:
                obs = st.text_input("Observaciones:", key=f"obs_{sub_item}", placeholder="Registrar hallazgo si aplica...", label_visibility="collapsed")
            
            respuestas_inspector[sub_item] = {"Resultado": estado, "Observaciones": obs}
        st.markdown("<br>", unsafe_allow_html=True)

    st.markdown("---")
    
    # === SECCIÓN 6: CONCLUSIÓN ===
    st.header("🏁 5. Dictamen Final del Organismo")
    dictamen_final = st.selectbox("Resultado de la Inspección (Dictamen Técnico):", ["APROBADO", "RECHAZADO", "APROBADO CONDICIONAL"])
    inspector_firma = st.text_input("Nombre y Firma Digital del Inspector Técnico Autorizado:")

    guardar_reporte = st.form_submit_button("🔒 Registrar Reporte de Inspección Oficial")

    if guardar_reporte:
        if not cliente or not serie or not inspector_firma:
            st.error("⚠️ Error de Integridad: Los campos 'Cliente', 'Serie del Equipo' y 'Firma del Inspector' son obligatorios.")
        elif not imparcialidad:
            st.error("❌ Bloqueo Normativo: No se puede generar un informe sin la declaración jurada de imparcialidad (ISO 17020 Cláusula 4.1).")
        else:
            id_reporte = f"{fecha.strftime('%Y%m%d')}-{random.randint(1000, 9999)}"
            
            cabecera = {"Fecha": str(fecha), "Cliente": cliente, "Ubicación": ubicacion, "Lugar": lugar_inspeccion}
            equipo = {"Marca": marca, "Modelo": modelo, "Serie": serie, "Año": anio_fab, "Interno": interno, "Patente": patente, "Chasis": n_chasis}
            tecnicos = {"Capacidad": capacidad_carga, "Radio": radio_trabajo, "Pluma": tipo_pluma, "Tren": tren_rodante}
            
            st.session_state.current_report = {
                "id": id_reporte, "cabecera": cabecera, "equipo": equipo, "tecnicos": tecnicos,
                "respuestas": respuestas_inspector, "dictamen": dictamen_final, "inspector": inspector_firma
            }
            
            registro_historico = {"Informe N°": f"INF-GM-{id_reporte}", "Fecha": str(fecha), "Cliente": cliente, "Equipo (Serie)": serie, "Dictamen": dictamen_final, "Inspector": inspector_firma}
            st.session_state.historial_inspecciones.append(registro_historico)
            st.success(f"✅ ¡Inspección guardada bajo registro de ANDES! Documentación disponible abajo.")

# --- SECCIÓN DE DESCARGA DE DOCUMENTOS EMITIDOS ---
if 'current_report' in st.session_state:
    st.markdown("---")
    st.header("📥 Descarga de Documentación Oficial (ISO 17020)")
    st.info("El reporte fue firmado digitalmente bajo los estándares de ANDES. Exportar evidencias objetivas:")
    
    rep = st.session_state.current_report
    
    pdf_informe = generar_pdf_informe(rep['cabecera'], rep['equipo'], rep['tecnicos'], rep['respuestas'], f"INF-GM-{rep['id']}", rep['dictamen'], rep['inspector'])
    pdf_certified = generar_pdf_certificado(rep['cabecera'], rep['equipo'], f"INF-GM-{rep['id']}", rep['dictamen'], rep['inspector'])
    
    col_d1, col_d2 = st.columns(2)
    with col_d1:
        st.download_button(
            label="📄 Descargar Informe Técnico ANDES (PDF)",
            data=pdf_informe,
            file_name=f"ANDES_Informe_Tecnico_GM_{rep['id']}.pdf",
            mime="application/pdf"
        )
    with col_d2:
        if rep['dictamen'] == "APROBADO":
            st.download_button(
                label="📜 Descargar Certificado de Aprobación ANDES (PDF)",
                data=pdf_certified,
                file_name=f"ANDES_Certificado_Aprobacion_GM_{rep['id']}.pdf",
                mime="application/pdf"
            )
        else:
            st.warning("⚠️ El Certificado no está disponible porque el dictamen final no es 'APROBADO'.")

# === SECCIÓN 7: HISTORIAL DE REGISTROS ===
st.markdown("---")
st.header("🗄️ Historial de Informes de Grúas Móviles")

if st.session_state.historial_inspecciones:
    st.dataframe(st.session_state.historial_inspecciones, use_container_width=True)
else:
    st.warning("No hay informes registrados en la sesión actual.")
