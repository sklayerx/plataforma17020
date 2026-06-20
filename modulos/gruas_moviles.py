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

# Estructura completa del checklist
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

    # Intentar descargar el logo
    try:
        req = urllib.request.Request(URL_LOGO, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req) as response:
            img_data = response.read()
        logo_pdf = Image(io.BytesIO(img_data), width=80, height=50)
    except Exception:
        logo_pdf = Paragraph("<b>ANDES</b>", title_style)

    header_text = Paragraph("<b>ANDES INGENIERÍA Y SERVICIOS</b><br/><font size=9 color='#1A3A5C'>ORGANISMO DE INSPECCIÓN - ISO/IEC 17020</font>", title_style)
    story.append(Table([[logo_pdf, header_text]], colWidths=[90, 450]))
    story.append(Spacer(1, 15))

    # Tabla 1: Datos de Control
    meta_data = [
        [Paragraph(f"<b>Informe N°:</b> {id_reporte}", cell_body), Paragraph(f"<b>Fecha:</b> {datos_cabecera['Fecha']}", cell_body)],
        [Paragraph(f"<b>Cliente:</b> {datos_cabecera['Cliente']}", cell_body), Paragraph(f"<b>Lugar:</b> {datos_cabecera['Lugar']}", cell_body)],
        [Paragraph(f"<b>Ubicación / Planta:</b> {datos_cabecera['Ubicación']}", cell_body), Paragraph("", cell_body)]
    ]
    t_meta = Table(meta_data, colWidths=[270, 270])
    t_meta.setStyle(TableStyle([
        ('BOX', (0,0), (-1,-1), 1, colors.HexColor('#0D1B2A')),
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor('#F4F6F9')),
        ('SPAN', (0,2), (1,2)),
        ('PADDING', (0,0), (-1,-1), 6)
    ]))
    story.append(t_meta)
    
    # Tabla 2: Información del Equipo
    story.append(Paragraph("DATOS DEL EQUIPO INSPECCIONADO", subtitle_style))
    equipo_data = [
        [Paragraph(f"<b>Marca:</b> {datos_equipo['Marca']}", cell_body), Paragraph(f"<b>Modelo:</b> {datos_equipo['Modelo']}", cell_body)],
        [Paragraph(f"<b>Serie N°:</b> {datos_equipo['Serie']}", cell_body), Paragraph(f"<b>Capacidad Nominal:</b> {datos_tecnicos['Capacidad']}", cell_body)],
        [Paragraph(f"<b>Longitud de Pluma:</b> {datos_tecnicos['Longitud']}", cell_body), Paragraph(f"<b>Horómetro actual:</b> {datos_tecnicos['Horómetro']}", cell_body)]
    ]
    t_equipo = Table(equipo_data, colWidths=[270, 270])
    t_equipo.setStyle(TableStyle([
        ('BOX', (0,0), (-1,-1), 1, colors.HexColor('#1A3A5C')),
        ('PADDING', (0,0), (-1,-1), 5)
    ]))
    story.append(t_equipo)

    # Tabla 3: Resultados del Checklist Técnico
    story.append(Paragraph("EVALUACIÓN CONFORME CRITERIOS DE ACEPTACIÓN / RECHAZO", subtitle_style))
    tabla_chk_data = [[Paragraph("<b>Criterio / Requisito Técnico Evaluado</b>", header_cell), Paragraph("<b>Resultado</b>", header_cell), Paragraph("<b>Observaciones Técnicas</b>", header_cell)]]
    
    for criterio, det in respuestas.items():
        tabla_chk_data.append([Paragraph(criterio, cell_body), Paragraph(det['Resultado'], cell_dictamen), Paragraph(det['Observaciones'], cell_body)])
        
    t_chk = Table(tabla_chk_data, colWidths=[280, 70, 190])
    t_chk.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#0D1B2A')),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#CBD5E0')),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('PADDING', (0,0), (-1,-1), 4)
    ]))
    story.append(t_chk)
    story.append(Spacer(1, 15))

    # Conclusión y Firmas
    story.append(Paragraph("DICTAMEN FINAL EVALUATIVO", subtitle_style))
    t_dict = Table([[Paragraph(f"<b>ESTADO DEL EQUIPO:</b> {dictamen}", cell_dictamen)]], colWidths=[540])
    color_bg = colors.HexColor('#C6F6D5') if dictamen == "APROBADO" else colors.HexColor('#FED7D7')
    t_dict.setStyle(TableStyle([
        ('BOX', (0,0), (-1,-1), 1.5, colors.HexColor('#0D1B2A')),
        ('BACKGROUND', (0,0), (-1,-1), color_bg),
        ('PADDING', (0,0), (-1,-1), 8)
    ]))
    story.append(t_dict)
    story.append(Spacer(1, 20))
    
    story.append(Paragraph(f"<b>Inspector Autorizado:</b> {inspector}", cell_body))
    story.append(Paragraph("<i>Firma digital registrada conforme la Cláusula 4.1 de Imparcialidad - ISO 17020</i>", cell_body))

    # Anexo Fotográfico (Si el usuario subió fotos)
    if lista_fotos:
        story.append(Spacer(1, 15))
        story.append(Paragraph("ANEXO FOTOGRÁFICO DE CAMPO", subtitle_style))
        tabla_fotos_data = []
        fila_actual = []
        for idx, foto_bytes in enumerate(lista_fotos):
            try:
                img_reader = ImageReader(io.BytesIO(foto_bytes))
                img_p = Image(img_reader, width=240, height=160)
                fila_actual.append(img_p)
                if len(fila_actual) == 2 or idx == len(lista_fotos) - 1:
                    if len(fila_actual) == 1:
                        fila_actual.append(Paragraph("", cell_body))
                    tabla_fotos_data.append(fila_actual)
                    fila_actual = []
            except:
                pass
        if tabla_fotos_data:
            t_fotos = Table(tabla_fotos_data, colWidths=[270, 270])
            t_fotos.setStyle(TableStyle([
                ('ALIGN', (0,0), (-1,-1), 'CENTER'),
                ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
                ('PADDING', (0,0), (-1,-1), 5)
            ]))
            story.append(t_fotos)

    doc.build(story)
    buffer.seek(0)
    return buffer

def desplegar_modulo_gruas(URL_LOGO):
    st.markdown("---")
    st.caption("Plataforma de Captura de Datos en Campo — Módulo: Grúas Móviles (GM)")
    
    st.sidebar.info("""
    **Procedimiento:** P-INS-01  
    **Formato:** Check List GM  
    **Alcance:** Grúas Móviles  
    """)

    # Formulario Unificado
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
            serie = st.text_input("Serie N°:")

        st.markdown("---")
        st.header("⚙️ 3. Especificaciones Técnicas y Operacionales")
        col5, col6 = st.columns(2)
        with col5:
            capacidad = st.text_input("Capacidad Nominal (Ej: 50 Ton):")
            longitud_pluma = st.text_input("Longitud de Pluma (Ej: 31 m):")
        with col6:
            horometro = st.text_input("Horómetro Actual:")

        st.markdown("---")
        st.header("🔍 4. Inspección de Requisitos Técnicos")
        
        respuestas_inspector = {}
        for categoria, sub_items in estructura_checklist.items():
            st.markdown(f"### 📍 {categoria}")
            for sub_item in sub_items:
                partes = sub_item.split(":", 1)
                st.markdown(f"**{partes[0]}** — *{partes[1].strip()}*")
                c_rad, c_obs = st.columns([2, 3])
                with c_rad:
                    estado = st.radio("Dictamen:", ["Cumple", "No Cumple", "No Aplica"], key=f"gm_{sub_item}", horizontal=True, label_visibility="collapsed")
                with c_obs:
                    obs = st.text_input("Observaciones específicas:", key=f"gm_obs_{sub_item}", label_visibility="collapsed")
                respuestas_inspector[partes[0]] = {"Resultado": estado, "Observaciones": obs}

        st.markdown("---")
        st.header("📸 5. Registro Fotográfico de Campo")
        # Reactivamos el File Uploader dentro del formulario
        fotos_subidas = st.file_uploader("Cargue las evidencias fotográficas de la inspección (Máx 4 imágenes):", type=["png", "jpg", "jpeg"], accept_multiple_files=True, key="uploader_gm")

        st.markdown("---")
        st.header("🔒 6. Cierre y Declaración de Conformidad")
        imparcialidad = st.checkbox("Declaro bajo juramento que mantengo absoluta imparcialidad e integridad técnica en esta inspección conforme a la Cláusula 4.1 de la norma ISO/IEC 17020.", key="gm_imp")
        dictamen_final = st.selectbox("Resultado de la Inspección (Dictamen Técnico):", ["APROBADO", "RECHAZADO"], key="gm_dict")
        inspector_firma = st.text_input("Firma Digital del Inspector Autorizado (Nombre Completo):", key="gm_firm")
        
        guardar_reporte = st.form_submit_button("🔒 Registrar Reporte Oficial GM y Generar PDF")

    # El procesamiento y las descargas se ejecutan FUERA del formulario usando variables de estado
    if guardar_reporte:
        if not cliente or not serie or not inspector_firma:
            st.error("⚠️ Los campos 'Cliente', 'Serie N°' y 'Firma Digital del Inspector' son obligatorios para emitir un documento oficial.")
        elif not imparcialidad:
            st.error("❌ No se puede registrar la inspección si no se acepta el compromiso bajo juramento de imparcialidad (ISO 17020).")
        else:
            id_reporte = f"GM-{random.randint(1000, 9999)}"
            
            # Convertir fotos cargadas a bytes
            lista_fotos_bytes = []
            if fotos_subidas:
                for f in fotos_subidas:
                    lista_fotos_bytes.append(f.read())
            
            # Agrupar los diccionarios
            cabecera = {"Fecha": str(fecha), "Cliente": cliente, "Lugar": lugar_inspeccion, "Ubicación": ubicacion}
            equipo = {"Marca": marca, "Modelo": modelo, "Serie": serie}
            tecnicos = {"Capacidad": capacidad, "Longitud": longitud_pluma, "Horómetro": horometro}
            
            # Generar el archivo PDF real usando ReportLab
            pdf_buffer = generar_pdf_informe(
                datos_cabecera=cabecera,
                datos_equipo=equipo,
                datos_tecnicos=tecnicos,
                respuestas=respuestas_inspector,
                id_reporte=id_reporte,
                dictamen=dictamen_final,
                inspector=inspector_firma,
                lista_fotos=lista_fotos_bytes,
                URL_LOGO=URL_LOGO
            )
            
            # Almacenar en la sesión del servidor para que no se pierda al refrescar
            st.session_state[f"pdf_{id_reporte}"] = pdf_buffer.getvalue()
            st.session_state.historial_inspecciones.append({
                "Informe N°": id_reporte,
                "Fecha": str(fecha),
                "Cliente": cliente,
                "Equipo (Serie)": serie,
                "Dictamen": dictamen_final,
                "Inspector": inspector_firma
            })
            
            st.success(f"✅ ¡Inspección de Grúa registrada exitosamente con el código de control **{id_reporte}**!")

    # Mostrar botones de descarga si hay reportes guardados en esta sesión
    for llave in list(st.session_state.keys()):
        if llave.startswith("pdf_"):
            id_rep = llave.replace("pdf_", "")
            st.markdown(f"### 📄 Descargar Documentación Oficial Emitida ({id_rep})")
            col_b1, col_b2 = st.columns(2)
            with col_b1:
                st.download_button(
                    label=f"⬇️ Descargar Informe de Inspección {id_rep} (PDF)",
                    data=st.session_state[llave],
                    file_name=f"Informe_Inspeccion_{id_rep}.pdf",
                    mime="application/pdf"
                )
            with col_b2:
                # El certificado reutiliza la estructura del PDF formal con el Dictamen correspondiente
                st.download_button(
                    label=f"📜 Descargar Certificado de Conformidad {id_rep} (PDF)",
                    data=st.session_state[llave],
                    file_name=f"Certificado_Conformidad_{id_rep}.pdf",
                    mime="application/pdf"
                )
