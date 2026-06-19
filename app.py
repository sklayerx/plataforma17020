import streamlit as st
import datetime
import random
import io
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors

# Configuración de la página
st.set_page_config(page_title="Inspección de Grúas Móviles - ISO 17020", layout="wide")

st.title("🛡️ Sistema de Gestión de Inspecciones (ISO/IEC 17020)")
st.caption("Plataforma Digital de Captura de Datos en Campo — Check List Grúas Móviles (GM)")

# Inicializar base de datos en sesión
if 'historial_inspecciones' not in st.session_state:
    st.session_state.historial_inspecciones = []

# --- PANEL LATERAL ---
st.sidebar.header("⚙️ Control de Operaciones")
st.sidebar.info("""
**Procedimiento:** P-INS-01  
**Formato:** Check List GM  
**Alcance:** Grúas Móviles  
**Estado:** Cumplimiento ISO 17020  
""")

# --- FUNCIONES PARA GENERACIÓN DE PDF (REQUISITO 7.4) ---
def generar_pdf_informe(datos_cabecera, datos_equipo, datos_tecnicos, respuestas, id_reporte, dictamen, inspector):
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter, rightMargin=40, leftMargin=40, topMargin=40, bottomMargin=40)
    story = []
    
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle('TitleStyle', parent=styles['Heading1'], fontSize=16, leading=20, alignment=1, textColor=colors.HexColor('#1A365D'))
    subtitle_style = ParagraphStyle('SubTitleStyle', parent=styles['Heading2'], fontSize=12, leading=16, textColor=colors.HexColor('#2B6CB0'), spaceBefore=10)
    body_style = styles['BodyText']
    
    # Encabezado Oficial
    story.append(Paragraph(f"<b>ORGANISMO DE INSPECCIÓN OFICIAL - ISO/IEC 17020</b>", title_style))
    story.append(Paragraph(f"INFORME TÉCNICO DE INSPECCIÓN DE SEGURIDAD EN GRÚAS MÓVILES", ParagraphStyle('Sub', parent=title_style, fontSize=11, spaceBefore=4)))
    story.append(Spacer(1, 15))
    
    # Tabla de metadatos del reporte
    meta_data = [
        [f"<b>Informe N°:</b> {id_reporte}", f"<b>Fecha:</b> {datos_cabecera['Fecha']}"],
        [f"<b>Cliente:</b> {datos_cabecera['Cliente']}", f"<b>Lugar:</b> {datos_cabecera['Lugar']}"],
        [f"<b>Ubicación:</b> {datos_cabecera['Ubicación']}", f"<b>Trazabilidad norm.:</b> {datos_cabecera['Trazabilidad']}"]
    ]
    t_meta = Table(meta_data, colWidths=[260, 260])
    t_meta.setStyle(TableStyle([('BOX', (0,0), (-1,-1), 1, colors.grey), ('INNERGRID', (0,0), (-1,-1), 0.5, colors.lightgrey), ('BACKGROUND', (0,0), (-1,-1), colors.HexColor('#F7FAFC'))]))
    story.append(t_meta)
    
    # Datos del Equipo y Técnicos
    story.append(Paragraph("<b>1. Identificación y Especificaciones Técnicas del Equipo</b>", subtitle_style))
    equipo_data = [
        [f"<b>Marca:</b> {datos_equipo['Marca']}", f"<b>Modelo:</b> {datos_equipo['Modelo']}", f"<b>N° Serie:</b> {datos_equipo['Serie']}"],
        [f"<b>Año Fab.:</b> {datos_equipo['Año']}", f"<b>Interno:</b> {datos_equipo['Interno']}", f"<b>Patente:</b> {datos_equipo['Patente']}"],
        [f"<b>N° Chasis:</b> {datos_equipo['Chasis']}", f"<b>Capacidad:</b> {datos_tecnicos['Capacidad']}", f"<b>Radio Trab.:</b> {datos_tecnicos['Radio']}"],
        [f"<b>Tipo Pluma:</b> {datos_tecnicos['Pluma']}", f"<b>Tren Rodante:</b> {datos_tecnicos['Tren']}", ""]
    ]
    t_eq = Table(equipo_data, colWidths=[173, 173, 174])
    t_eq.setStyle(TableStyle([('BOX', (0,0), (-1,-1), 1, colors.grey), ('INNERGRID', (0,0), (-1,-1), 0.5, colors.lightgrey)]))
    story.append(t_eq)
    
    # Tabla de Resultados del Checklist
    story.append(Paragraph("<b>2. Desglose de Hallazgos y Evaluación Técnica</b>", subtitle_style))
    check_data = [["<b>Ítem / Componente Evaluado</b>", "<b>Dictamen</b>", "<b>Observaciones / Hallazgos</b>"]]
    
    for item, resp in respuestas.items():
        # Limpiar texto para evitar cortes
        item_corto = item.split(":", 1)[0]
        check_data.append([Paragraph(item_corto, body_style), resp['Resultado'], Paragraph(resp['Observaciones'] if resp['Observaciones'] else "Sin novedades", body_style)])
        
    t_check = Table(check_data, colWidths=[180, 70, 270])
    t_check.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#2B6CB0')),
        ('TEXTCOLOR', (0,0), (-1,0), colors.white),
        ('ALIGN', (0,0), (-1,0), 'CENTER'),
        ('BOTTOMPADDING', (0,0), (-1,0), 6),
        ('GRID', (0,0), (-1,-1), 0.5, colors.grey),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE')
    ]))
    story.append(t_check)
    
    # Conclusión
    story.append(Paragraph("<b>3. Dictamen Final y Firmas</b>", subtitle_style))
    concl_data = [
        [f"<b>DICTAMEN TÉCNICO FINAL:</b> {dictamen}"],
        [f"<b>Inspector Autorizado:</b> {inspector}"],
        ["<i>Este documento se emite bajo las condiciones de confidencialidad e imparcialidad exigidas por la norma ISO/IEC 17020.</i>"]
    ]
    t_concl = Table(concl_data, colWidths=[520])
    t_concl.setStyle(TableStyle([('BOX', (0,0), (-1,-1), 1.5, colors.HexColor('#1A365D')), ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#EDF2F7')), ('PADDING', (0,0), (-1,-1), 8)]))
    story.append(t_concl)
    
    doc.build(story)
    buffer.seek(0)
    return buffer

def generar_pdf_certificado(datos_cabecera, datos_equipo, id_reporte, dictamen, inspector):
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter, rightMargin=50, leftMargin=50, topMargin=50, bottomMargin=50)
    story = []
    
    styles = getSampleStyleSheet()
    cert_title = ParagraphStyle('CertTitle', parent=styles['Heading1'], fontSize=22, leading=26, alignment=1, textColor=colors.HexColor('#1A365D'), spaceAfter=20)
    cert_body = ParagraphStyle('CertBody', parent=styles['BodyText'], fontSize=12, leading=20, alignment=4, spaceBefore=15)
    
    story.append(Spacer(1, 40))
    story.append(Paragraph("<b>CERTIFICADO DE INSPECCIÓN Y APROBACIÓN</b>", cert_title))
    story.append(Paragraph(f"<b>Certificado N°:</b> CERT-{id_reporte}", ParagraphStyle('Sub', alignment=1, fontSize=11)))
    story.append(Spacer(1, 30))
    
    texto = f"El <b>Organismo de Inspección Técnica</b>, en cumplimiento estricto con los procedimientos de evaluación y los requisitos de la norma de referencia, certifica que se ha realizado la inspección de seguridad física y operativa sobre el equipo que se detalla a continuación:"
    story.append(Paragraph(texto, cert_body))
    story.append(Spacer(1, 20))
    
    eq_info = [
        ["<b>Propietario / Cliente:</b>", datos_cabecera['Cliente']],
        ["<b>Equipo / Máquina:</b>", "Grúa Móvil"],
        ["<b>Marca y Modelo:</b>", f"{datos_equipo['Marca']} / {datos_equipo['Modelo']}"],
        ["<b>Número de Serie:</b>", datos_equipo['Serie']],
        ["<b>Identificación Interna / Patente:</b>", f"{datos_equipo['Interno']} / {datos_equipo['Patente']}"]
    ]
    t_eq = Table(eq_info, colWidths=[200, 270])
    t_eq.setStyle(TableStyle([('GRID', (0,0), (-1,-1), 0.5, colors.lightgrey), ('PADDING', (0,0), (-1,-1), 8), ('BACKGROUND', (0,0), (0,-1), colors.HexColor('#EDF2F7'))]))
    story.append(t_eq)
    
    story.append(Spacer(1, 25))
    status_color = "#38A169" if dictamen == "APROBADO" else "#DD6B20"
    texto_dictamen = f"Luego de concluir los ensayos y listas de verificación de campo, el dictamen conclusivo del organismo es: <font color='{status_color}'><b>{dictamen}</b></font>."
    story.append(Paragraph(texto_dictamen, cert_body))
    
    texto_val = f"<b>Fecha de Emisión:</b> {datos_cabecera['Fecha']}<br/><b>Vigencia recomendada:</b> 1 Año a partir de la fecha de emisión conforme a las directrices de seguridad internacionales."
    story.append(Paragraph(texto_val, cert_body))
    
    story.append(Spacer(1, 60))
    story.append(Paragraph(f"_______________________________________<br/><b>{inspector}</b><br/>Inspector Técnico Autorizado", ParagraphStyle('Firma', alignment=1, fontSize=11)))
    
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
        ubicacion = st.text_input("Ubicación:")
    with col2:
        lugar_inspeccion = st.text_input("Lugar de inspección:")
        trazabilidad = st.text_input("Trazabilidad (Código Interno/Procedimiento):")

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
    
    # === SECCIÓN 4: CONTROL DE IMPARCIALIDAD ===
    st.subheader("⚖️ Control de Imparcialidad e Independencia (Requisito 4.1)")
    imparcialidad = st.checkbox("Declaro formalmente que no poseo conflictos de interés comerciales, financieros ni técnicos respecto al ítem evaluado.")

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
            
            # Agrupar diccionarios para los generadores de PDF
            cabecera = {"Fecha": str(fecha), "Cliente": cliente, "Ubicación": ubicacion, "Lugar": lugar_inspeccion, "Trazabilidad": trazabilidad}
            equipo = {"Marca": marca, "Modelo": modelo, "Serie": serie, "Año": anio_fab, "Interno": interno, "Patente": patente, "Chasis": n_chasis}
            tecnicos = {"Capacidad": capacidad_carga, "Radio": radio_trabajo, "Pluma": tipo_pluma, "Tren": tren_rodante}
            
            # Guardar en estado de sesión para persistencia temporal en pantalla
            st.session_state.current_report = {
                "id": id_reporte, "cabecera": cabecera, "equipo": equipo, "tecnicos": tecnicos,
                "respuestas": respuestas_inspector, "dictamen": dictamen_final, "inspector": inspector_firma
            }
            
            registro_historico = {"Informe N°": f"INF-GM-{id_reporte}", "Fecha": str(fecha), "Cliente": cliente, "Equipo (Serie)": serie, "Dictamen": dictamen_final, "Inspector": inspector_firma}
            st.session_state.historial_inspecciones.append(registro_historico)
            st.success(f"✅ ¡Inspección guardada! Códigos listos para descarga abajo.")

# --- SECCIÓN DE DESCARGA DE DOCUMENTOS EMITIDOS ---
if 'current_report' in st.session_state:
    st.markdown("---")
    st.header("📥 Descarga de Documentación Oficial (ISO 17020)")
    st.info("El reporte fue firmado digitalmente. Utilice los siguientes botones para exportar las evidencias objetivas.")
    
    rep = st.session_state.current_report
    
    # Generar PDFs en memoria
    pdf_informe = generar_pdf_informe(rep['cabecera'], rep['equipo'], rep['tecnicos'], rep['respuestas'], f"INF-GM-{rep['id']}", rep['dictamen'], rep['inspector'])
    pdf_certificado = generar_pdf_certificado(rep['cabecera'], rep['equipo'], f"INF-GM-{rep['id']}", rep['dictamen'], rep['inspector'])
    
    col_d1, col_d2 = st.columns(2)
    with col_d1:
        st.download_button(
            label="📄 Descargar Informe Técnico Detallado (PDF)",
            data=pdf_informe,
            file_name=f"Informe_Tecnico_GM_{rep['id']}.pdf",
            mime="application/pdf"
        )
    with col_d2:
        # Solo permitir el certificado formal si el equipo fue efectivamente APROBADO
        if rep['dictamen'] == "APROBADO":
            st.download_button(
                label="📜 Descargar Certificado de Aprobación (PDF)",
                data=pdf_certificado,
                file_name=f"Certificado_Aprobacion_GM_{rep['id']}.pdf",
                mime="application/pdf"
            )
        else:
            st.warning("⚠️ El Certificado de Aprobación no está disponible porque el dictamen final no es 'APROBADO'.")

# === SECCIÓN 7: HISTORIAL DE REGISTROS ===
st.markdown("---")
st.header("🗄️ Historial de Informes de Grúas Móviles")

if st.session_state.historial_inspecciones:
    st.dataframe(st.session_state.historial_inspecciones, use_container_width=True)
else:
    st.warning("No hay informes registrados en la sesión actual.")
