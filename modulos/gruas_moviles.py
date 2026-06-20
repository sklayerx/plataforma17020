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

# --- ESTRUCTURA MAESTRA DEL CHECKLIST ORIGINAL ---
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
        "Frenos y embragues: Revisar el funcionamiento de los sistemas de frenado de izaje, giro y tras lación.",
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

# --- FUNCIONES DE GENERACIÓN DE PDF ORIGINALES COMPLETAS ---
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
    
    meta_data = [
        [Paragraph(f"<b>Informe N°:</b> {id_reporte}", cell_body), Paragraph(f"<b>Fecha:</b> {datos_cabecera['Fecha']}", cell_body)],
        [Paragraph(f"<b>Cliente:</b> {datos_cabecera['Cliente']}", cell_body), Paragraph(f"<b>Lugar:</b> {datos_cabecera['Lugar']}", cell_body)],
        [Paragraph(f"<b>Ubicación / Planta:</b> {datos_cabecera['Ubicación']}", cell_body), Paragraph("", cell_body)]
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
    
    story.append(Paragraph("1. Identificación y Especificaciones Técnicas del Equipo", subtitle_style))
    equipo_data = [
        [Paragraph(f"<b>Marca:</b> {datos_equipo['Marca']}", cell_body), Paragraph(f"<b>Modelo:</b> {datos_equipo['Modelo']}", cell_body), Paragraph(f"<b>N° Serie:</b> {datos_equipo['Serie']}", cell_body)],
        [Paragraph(f"<b>Año Fab.:</b> {datos_equipo['Año']}", cell_body), Paragraph(f"<b>Interno:</b> {datos_equipo['Interno']}", cell_body), Paragraph(f"<b>Patente:</b> {datos_equipo['Patente']}", cell_body)],
        [Paragraph(f"<b>N° Chasis:</b> {datos_equipo['Chasis']}", cell_body), Paragraph(f"<b>Capacidad:</b> {datos_tecnicos['Capacidad']}", cell_body), Paragraph(f"<b>Radio Trab.:</b> {datos_tecnicos['Radio']}", cell_body)],
        [Paragraph(f"<b>Tipo Pluma:</b> {datos_tecnicos['Pluma']}", cell_body), Paragraph(f"<b>Tren Rodante:</b> {datos_tecnicos['Tren']}", cell_body), Paragraph("", cell_body)]
    ]
    t_eq = Table(equipo_data, colWidths=[180, 180, 180])
    t_eq.setStyle(TableStyle([
        ('BOX', (0,0), (-1,-1), 1, colors.HexColor('#1A3A5C')), 
        ('INNERGRID', (0,0), (-1,-1), 0.5, colors.HexColor('#F4F6F9')), 
        ('PADDING', (0,0), (-1,-1), 5),
        ('SPAN', (0,3), (1,3))
    ]))
    story.append(t_eq)
    
    story.append(Paragraph("2. Evaluación Técnica y Hallazgos de Campo", subtitle_style))
    check_data = [[
        Paragraph("<b>Ítem / Componente Evaluado</b>", header_cell), 
        Paragraph("<b>Dictamen</b>", header_cell), 
        Paragraph("<b>Observaciones / Hallazgos</b>", header_cell)
    ]]
    
    indices_categorias = []
    fila_cont = 1
    for categoria, sub_items in estructura_checklist.items():
        check_data.append([Paragraph(f"<b>📍 {categoria}</b>", cat_cell_style), "", ""])
        indices_categorias.append(fila_cont)
        fila_cont += 1
        
        for sub_item in sub_items:
            partes = sub_item.split(":", 1)
            titulo_item = f"<b>{partes[0]}</b>"
            if len(partes) > 1:
                titulo_item += f": {partes[1]}"
            
            resp = respuestas.get(sub_item, {"Resultado": "N/A", "Observaciones": "Sin registrar"})
            
            check_data.append([
                Paragraph(titulo_item, cell_body), 
                Paragraph(resp['Resultado'], cell_dictamen), 
                Paragraph(resp['Observaciones'] if resp['Observaciones'] else "Sin novedades registradas", cell_body)
            ])
            fila_cont += 1
        
    t_check = Table(check_data, colWidths=[210, 70, 260])
    estilos_tabla = [
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#0D1B2A')),
        ('ALIGN', (0,0), (-1,0), 'CENTER'),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#1A3A5C')),
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ('TOPPADDING', (0,0), (-1,-1), 6),
        ('BOTTOMPADDING', (0,0), (-1,-1), 6),
        ('LEFTPADDING', (0,0), (-1,-1), 5),
        ('RIGHTPADDING', (0,0), (-1,-1), 5)
    ]
    
    for idx in indices_categorias:
        estilos_tabla.append(('SPAN', (0, idx), (2, idx)))
        estilos_tabla.append(('BACKGROUND', (0, idx), (2, idx), colors.HexColor('#EDF2F7')))
        estilos_tabla.append(('TOPPADDING', (0, idx), (2, idx), 7))
        estilos_tabla.append(('BOTTOMPADDING', (0, idx), (2, idx), 7))
        
    t_check.setStyle(TableStyle(estilos_tabla))
    story.append(t_check)

    # REPARACIÓN DE LAS FOTOS: Procesamiento exacto
    if lista_fotos:
        story.append(Spacer(1, 15))
        story.append(Paragraph("3. Registro Fotográfico de Evidencias (Evidencia Objetiva)", subtitle_style))
        
        fotos_tabla = []
        fila_actual = []
        for foto_archivo in lista_fotos:
            try:
                # Recuperar los bytes completos del objeto UploadedFile
                bytes_foto = foto_archivo.getvalue() if hasattr(foto_archivo, 'getvalue') else foto_archivo
                img_reader = ImageReader(io.BytesIO(bytes_foto))
                ancho_orig, alto_orig = img_reader.getSize()
                alto_calculado = (alto_orig * 240) / ancho_orig
                
                dibujo_foto = Image(io.BytesIO(bytes_foto), width=240, height=alto_calculado)
                nombre_foto = foto_archivo.name if hasattr(foto_archivo, 'name') else "Evidencia de Campo"
                celda_foto = [dibujo_foto, Spacer(1, 3), Paragraph(f"Evidencia: {nombre_foto}", ParagraphStyle('FotoLabel', parent=cell_body, fontSize=7, alignment=1))]
                fila_actual.append(celda_foto)
            except Exception:
                pass
            if len(fila_actual) == 2:
                fotos_tabla.append(fila_actual)
                fila_actual = []
        if fila_actual:
            fila_actual.append("")
            fotos_tabla.append(fila_actual)
        if fotos_tabla:
            t_fotos = Table(fotos_tabla, colWidths=[270, 270])
            t_fotos.setStyle(TableStyle([
                ('ALIGN', (0,0), (-1,-1), 'CENTER'), ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
                ('TOPPADDING', (0,0), (-1,-1), 10), ('BOTTOMPADDING', (0,0), (-1,-1), 10)
            ]))
            story.append(t_fotos)
    
    story.append(Spacer(1, 15))
    story.append(Paragraph("4. Conclusión de la Inspección y Firmas", subtitle_style))
    concl_data = [
        [Paragraph(f"<b>DICTAMEN TÉCNICO FINAL:</b> {dictamen}", ParagraphStyle('FinalD', parent=cell_body, fontSize=10))],
        [Paragraph(f"<b>Inspector Técnico Autorizado:</b> {inspector}", ParagraphStyle('FinalI', parent=cell_body, fontSize=9))],
        [Paragraph("<i>Este documento confidencial es emitido por ANDES Ingeniería y Servicios bajo las directrices de la norma ISO/IEC 17020.</i>", ParagraphStyle('FinalN', parent=cell_body, fontSize=7.5))]
    ]
    t_concl = Table(concl_data, colWidths=[540])
    t_concl.setStyle(TableStyle([
        ('BOX', (0,0), (-1,-1), 1.5, colors.HexColor('#0D1B2A')), ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#F4F6F9')), ('PADDING', (0,0), (-1,-1), 6)
    ]))
    story.append(t_concl)
    
    doc.build(story)
    buffer.seek(0)
    return buffer

def generar_pdf_certificado(datos_cabecera, datos_equipo, id_reporte, dictamen, inspector, URL_LOGO):
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
    
    texto = f"El <b>Organismo de Inspección de ANDES Ingeniería y Servicios</b>, conforme con los esquemas de evaluación normativos correspondientes, certifica que se ha ejecutado el protocolo de inspection de seguridad física y estructural sobre el siguiente ítem:"
    story.append(Paragraph(texto, cert_body))
    story.append(Spacer(1, 15))
    
    eq_info = [
        [Paragraph("<b>Propietario / Cliente:</b>", cert_body), Paragraph(datos_cabecera['Cliente'], cert_body)],
        [Paragraph("<b>Categoría de Equipo:</b>", cert_body), Paragraph("Grúa Móvil (Módulo GM)", cert_body)],
        [Paragraph("<b>Marca / Modelo:</b>", cert_body), Paragraph(f"{datos_equipo['Marca']} / {datos_equipo['Modelo']}", cert_body)],
        [Paragraph("<b>Número de Serie / Chasis:</b>", cert_body), Paragraph(f"{datos_equipo['Serie']} / {datos_equipo['Chasis']}", cert_body)],
        [Paragraph("<b>Identificación Interna / Dominio:</b>", cert_body), Paragraph(f"{datos_equipo['Interno']} / {datos_equipo['Patente']}", cert_body)]
    ]
    t_eq = Table(eq_info, colWidths=[200, 270])
    t_eq.setStyle(TableStyle([
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#1A3A5C')), ('PADDING', (0,0), (-1,-1), 8),
        ('BACKGROUND', (0,0), (0,-1), colors.HexColor('#F4F6F9')), ('BOX', (0,0), (-1,-1), 1.5, colors.HexColor('#0D1B2A')),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE')
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

# --- INTERFAZ COMPLETA DEL SUBMÓDULO ---
def desplegar_modulo_gruas(URL_LOGO):
    st.markdown("---")
    st.caption("Plataforma de Captura de Datos en Campo — Módulo: Grúas Móviles (GM)")

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
        st.header("⚙️ 3. Datos Técnicos")
        col5, col6 = st.columns(2)
        with col5:
            capacidad_carga = st.text_input("Capacidad de carga:")
            radio_trabajo = st.text_input("Radio de trabajo:")
        with col6:
            tipo_pluma = st.text_input("Tipo de pluma:")
            tren_rodante = st.text_input("Tren rodante:")

        st.markdown("---")
        st.subheader("⚖️ Control de Imparcialidad e Independencia")
        imparcialidad = st.checkbox("Declaro formalmente bajo juramento que no poseo conflictos de interés comerciales, financieros ni técnicos respecto al ítem evaluado.", key="gm_imp_chk")

        st.markdown("---")
        st.header("🔍 4. Inspección de Requisitos Técnicos")
        st.info("Seleccione la calificación para cada sub-ítem y registre observaciones en caso de desvíos.")

        respuestas_inspector = {}

        # Renderizado dinámico respetando leyendas largas de la plataforma original
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
        st.header("📸 5. Registro Fotográfico Opcional")
        fotos_cargadas = st.file_uploader(
            "Siga las pautas del instructivo de ANDES: Adjunte fotografías nítidas de desvíos críticos o placas identificatorias.",
            type=["png", "jpg", "jpeg"],
            accept_multiple_files=True,
            key="fotos_gruas_uploader"
        )

        st.markdown("---")
        st.header("🏁 6. Dictamen Final del Organismo")
        dictamen_final = st.selectbox("Resultado de la Inspección (Dictamen Técnico):", ["APROBADO", "RECHAZADO", "APROBADO CONDICIONAL"], key="gm_dict_sel")
        inspector_firma = st.text_input("Nombre y Firma Digital del Inspector Técnico Autorizado:", key="gm_firm_txt")

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
                
                # Guardamos en Session State usando una clave estructurada
                st.session_state.current_report = {
                    "id": id_reporte, "cabecera": cabecera, "equipo": equipo, "tecnicos": tecnicos,
                    "respuestas": respuestas_inspector, "dictamen": dictamen_final, "inspector": inspector_firma,
                    "fotos": fotos_cargadas if fotos_cargadas else []
                }
                
                registro_historico = {"Informe N°": f"INF-GM-{id_reporte}", "Fecha": str(fecha), "Cliente": cliente, "Equipo (Serie)": serie, "Dictamen": dictamen_final, "Inspector": inspector_firma}
                st.session_state.historial_inspecciones.append(registro_historico)
                st.success(f"✅ ¡Inspección guardada bajo registro de ANDES! Documentación disponible abajo.")

    # Renderizado y generación del informe fuera del form para evitar recargas erróneas
    if 'current_report' in st.session_state:
        st.markdown("---")
        st.header("📥 Descarga de Documentación Oficial (ISO 17020)")
        st.info("El reporte fue firmado digitalmente bajo los estándares de ANDES. Exportar evidencias objetivas:")
        
        rep = st.session_state.current_report
        
        pdf_informe = generar_pdf_informe(rep['cabecera'], rep['equipo'], rep['tecnicos'], rep['respuestas'], f"INF-GM-{rep['id']}", rep['dictamen'], rep['inspector'], rep['fotos'], URL_LOGO)
        pdf_certified = generar_pdf_certificado(rep['cabecera'], rep['equipo'], f"INF-GM-{rep['id']}", rep['dictamen'], rep['inspector'], URL_LOGO)
        
        col_d1, col_d2 = st.columns(2)
        with col_d1:
            st.download_button(
                label="📄 Descargar Informe Técnico ANDES con Fotos (PDF)",
                data=pdf_informe,
                file_name=f"ANDES_Informe_Tecnico_GM_{rep['id']}.pdf",
                mime="application/pdf",
                key="btn_descarga_inf"
            )
        with col_d2:
            if rep['dictamen'] == "APROBADO":
                st.download_button(
                    label="📜 Descargar Certificado de Aprobación ANDES (PDF)",
                    data=pdf_certified,
                    file_name=f"ANDES_Certificado_Aprobacion_GM_{rep['id']}.pdf",
                    mime="application/pdf",
                    key="btn_descarga_cert"
                )
            else:
                st.warning("⚠️ El Certificado no está disponible porque el dictamen final no es 'APROBADO'.")

    st.markdown("---")
    st.header("🗄️ Historial de Informes de Grúas Móviles")
    if st.session_state.historial_inspecciones:
        st.dataframe(st.session_state.historial_inspecciones, use_container_width=True)
    else:
        st.warning("No hay informes registrados en la sesión actual.")
