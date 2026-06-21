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

# --- ESTRUCTURA MAESTRA DEL CHECKLIST (ASME B30.22) ---
estructura_checklist_gpa = {
    "A. Documentación e Información Técnica": [
        "A. Doc.1. Tablas de Capacidad de Carga: Deben estar completamente legibles, visibles para el operador y fijadas firmemente al equipo (Sec. 22-1.1.3).",
        "A. Doc.2. Manual de Operación y Placas: Manual disponible en el equipo en el idioma correspondiente. Placas con datos del fabricante, modelo y número de serie legibles.",
        "A. Doc.3. Marcas de Advertencia y Calcomanías: Calcomanías de peligro (ej. electrocución, atrapamiento) visibles y legibles en las zonas críticas de operación."
    ],
    "B. Componentes Estructurales y Estabilidad": [
        "B. Est.4. Mecanismos de Elevación de Pluma: Inspección de la pluma interna, externa y plumín (jib) buscando deformaciones, fisuras o abolladuras (Sec. 22-1.2.1).",
        "B. Est.5. Plumas Telescópicas: Verificación de las secciones telescópicas, desgaste en almohadillas de deslizamiento (wear pads) y alineación (Sec. 22-1.2.2).",
        "B. Est.6. Estructura de Montaje y Chasis: Inspección de los pernos de anclaje de la base de la grúa al chasis del camión, buscando torque correcto y ausencia de fisuras en soldaduras.",
        "B. Est.7. Sistema de Estabilizadores: Inspección visual de vigas de extensión y gatos estabilizadores. Ausencia de deformaciones estructurales."
    ],
    "C. Potencia y Mecanismos de Operación": [
        "C. Pot.8. Control de Giro (Swing Control): Inspección del mecanismo de rotación, juego excesivo en la corona de giro, estado de los pernos y funcionamiento del freno de giro (Sec. 22-1.3.1).",
        "C. Pot.9. Mandos de Operación: Palancas y joysticks deben regresar a su posición neutral automáticamente al soltarse. Rotulación clara de funciones."
    ],
    "D. Sistema Hidráulico": [
        "D. Hid.10. Cilindros Hidráulicos: Inspección de cilindros de elevación, extensión y estabilizadores para detectar fugas de aceite en sellos y daños en vástagos.",
        "D. Hid.11. Válvulas de Retención de Carga: Los cilindros deben contar con válvulas de retención de carga (load holding check valves) operativas para evitar movimientos incontrolados en caso de pérdida de presión (Sec. 22-1.2.1).",
        "D. Hid.12. Mangueras y Conexiones: Ausencia de fugas, ampollas, grietas, rozamiento mecánico o deformaciones en líneas de alta presión. Nivel óptimo de aceite en tanque."
    ],
    "E. Sistemas de Izaje y Elementos Relacionados": [
        "E. Iza.13. Mecanismo de Izaje (Malacate): Si está equipado con malacate, verificar fijación, estado del tambor, bridas con una extensión mínima de 1/2\" sobre la última capa de cable (Sec. 22-1.2.3).",
        "E. Iza.14. Poleas y Guías: Inspección de ranuras de poleas, desgaste excesivo y presencia de pasadores/guardas para evitar que el cable se salga de la ranura.",
        "E. Iza.15. Cable de Acero: Inspección de hilos rotos, cocas, corrosión, aplastamientos y medición dimensional del diámetro conforme a ASME B30.30.",
        "E. Iza.16. Gancho de Carga: Inspección visual de fisuras, deformación angular o apertura de la garganta mayor al 5%. Debe contar con pestillo de seguridad operativo (ASME B30.10)."
    ],
    "F. Dispositivos de Seguridad": [
        "F. Seg.17. Dispositivos de Parada de Emergencia: Funcionamiento correcto de los botones de parada de emergencia (E-Stops) interrumpiendo todas las funciones motrices.",
        "F. Seg.18. Ayudas Operativas / Indicadores: Indicadores de ángulo de pluma, alarmas audibles/visuales y limitadores de capacidad nominal (si aplica) operativos."
    ],
    "G. Ensayos y Pruebas Operacionales": [
        "G. Pru.19. Prueba Operacional (Sin Carga): Verificación funcional completa de todos los movimientos de la pluma (extender, retraer, elevar, girar) y de los estabilizadores.",
        "G. Pru.20. Ensayo del Sistema de Bloqueo: Simular o verificar el funcionamiento de las válvulas anticaída sosteniendo la posición de la pluma sin comandos activos."
    ]
}

# --- MOTORES DE GENERACIÓN DE RENDERS PDF PARA GPA ---
def generar_pdf_informe_gpa(datos_cabecera, datos_equipo, datos_tecnicos, respuestas, id_reporte, dictamen, inspector, lista_fotos, URL_LOGO):
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter, rightMargin=36, leftMargin=36, topMargin=36, bottomMargin=36)
    story = []
    
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle('GPA_Title', parent=styles['Heading1'], fontSize=15, leading=18, textColor=colors.HexColor('#0D1B2A'))
    subtitle_style = ParagraphStyle('GPA_SubTitle', parent=styles['Heading2'], fontSize=11, leading=15, textColor=colors.HexColor('#1A3A5C'), spaceBefore=12, spaceAfter=6)
    cell_body = ParagraphStyle('CellBodyGPA', parent=styles['Normal'], fontSize=8.5, leading=12, textColor=colors.HexColor('#2D3748'))
    cell_dictamen = ParagraphStyle('CellDictGPA', parent=styles['Normal'], fontSize=9, leading=12, alignment=1, textColor=colors.HexColor('#0D1B2A'))
    header_cell = ParagraphStyle('HeaderCellGPA', parent=styles['Normal'], fontSize=9, leading=12, alignment=1, textColor=colors.white)
    cat_cell_style = ParagraphStyle('CatCellGPA', parent=styles['Normal'], fontSize=9, leading=12, textColor=colors.HexColor('#0D1B2A'))

    try:
        req = urllib.request.Request(URL_LOGO, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req) as response:
            img_data = response.read()
        logo_pdf = Image(io.BytesIO(img_data), width=80, height=50)
    except Exception:
        logo_pdf = Paragraph("<b>ANDES</b>", title_style)

    header_text = Paragraph("""
        <b>ANDES INGENIERÍA Y SERVICIOS</b><br/>
        <font size=9 color='#1A3A5C'>ORGANISMO DE INSPECCIÓN ACREDITADO - ISO/IEC 17020</font><br/>
        <font size=10 color='#0D1B2A'>INFORME TÉCNICO DE INSPECCIÓN — GRÚAS DE PLUMA ARTICULADA (ASME B30.22)</font>
    """, title_style)
    
    story.append(Table([[logo_pdf, header_text]], colWidths=[90, 450]))
    story.append(Spacer(1, 5))
    
    meta_data = [
        [Paragraph(f"<b>Informe N°:</b> {id_reporte}", cell_body), Paragraph(f"<b>Fecha:</b> {datos_cabecera['Fecha']}", cell_body)],
        [Paragraph(f"<b>Cliente:</b> {datos_cabecera['Cliente']}", cell_body), Paragraph(f"<b>Lugar:</b> {datos_cabecera['Lugar']}", cell_body)],
        [Paragraph(f"<b>Ubicación / Planta:</b> {datos_cabecera['Ubicación']}", cell_body), Paragraph("", cell_body)]
    ]
    t_meta = Table(meta_data, colWidths=[270, 270])
    t_meta.setStyle(TableStyle([
        ('BOX', (0,0), (-1,-1), 1, colors.HexColor('#0D1B2A')), ('INNERGRID', (0,0), (-1,-1), 0.5, colors.HexColor('#1A3A5C')),
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor('#F4F6F9')), ('PADDING', (0,0), (-1,-1), 5), ('SPAN', (0,2), (1,2))
    ]))
    story.append(t_meta)
    
    story.append(Paragraph("1. Identificación y Especificaciones Técnicas de la Unidad Articulada", subtitle_style))
    equipo_data = [
        [Paragraph(f"<b>Marca Grúa:</b> {datos_equipo['Marca']}", cell_body), Paragraph(f"<b>Modelo Grúa:</b> {datos_equipo['Modelo']}", cell_body), Paragraph(f"<b>N° Serie:</b> {datos_equipo['Serie']}", cell_body)],
        [Paragraph(f"<b>Año Fab.:</b> {datos_equipo['Año']}", cell_body), Paragraph(f"<b>Interno / Código:</b> {datos_equipo['Interno']}", cell_body), Paragraph(f"<b>Camión (Patente):</b> {datos_equipo['Patente']}", cell_body)],
        [Paragraph(f"<b>Capacidad Máx.:</b> {datos_tecnicos['Capacidad']}", cell_body), Paragraph(f"<b>Alcance Máx.:</b> {datos_tecnicos['Alcance']}", cell_body), Paragraph(f"<b>N° Estabilizadores:</b> {datos_tecnicos['Estabilizadores']}", cell_body)]
    ]
    t_eq = Table(equipo_data, colWidths=[180, 180, 180])
    t_eq.setStyle(TableStyle([
        ('BOX', (0,0), (-1,-1), 1, colors.HexColor('#1A3A5C')), ('INNERGRID', (0,0), (-1,-1), 0.5, colors.HexColor('#F4F6F9')), ('PADDING', (0,0), (-1,-1), 5)
    ]))
    story.append(t_eq)
    
    story.append(Paragraph("2. Evaluación Conforme Criterios ASME B30.22", subtitle_style))
    check_data = [[Paragraph("<b>Código / Requisito Técnico Evaluado</b>", header_cell), Paragraph("<b>Dictamen</b>", header_cell), Paragraph("<b>Observaciones / Hallazgos</b>", header_cell)]]
    
    indices_categorias = []
    fila_cont = 1
    for categoria, sub_items in respuestas.items():
        check_data.append([Paragraph(f"<b>📍 {categoria}</b>", cat_cell_style), "", ""])
        indices_categorias.append(fila_cont)
        fila_cont += 1
        
        for item_key, values in sub_items.items():
            check_data.append([Paragraph(item_key, cell_body), Paragraph(values['Resultado'], cell_dictamen), Paragraph(values['Observaciones'] if values['Observaciones'] else "Sin novedades registradas", cell_body)])
            fila_cont += 1
        
    t_check = Table(check_data, colWidths=[230, 65, 245])
    estilos_tabla = [
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#0D1B2A')), ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#1A3A5C')),
        ('VALIGN', (0,0), (-1,-1), 'TOP'), ('TOPPADDING', (0,0), (-1,-1), 5), ('BOTTOMPADDING', (0,0), (-1,-1), 5)
    ]
    for idx in indices_categorias:
        estilos_tabla.append(('SPAN', (0, idx), (2, idx)))
        estilos_tabla.append(('BACKGROUND', (0, idx), (2, idx), colors.HexColor('#EDF2F7')))
    t_check.setStyle(TableStyle(estilos_tabla))
    story.append(t_check)

    # Registro fotográfico
    if lista_fotos:
        story.append(Spacer(1, 15))
        story.append(Paragraph("3. Evidencia Objetiva Adjunta (Registro Fotográfico)", subtitle_style))
        fotos_tabla = []
        fila_actual = []
        for foto_archivo in lista_fotos:
            try:
                bytes_foto = foto_archivo.getvalue() if hasattr(foto_archivo, 'getvalue') else foto_archivo
                img_reader = ImageReader(io.BytesIO(bytes_foto))
                ancho_orig, alto_orig = img_reader.getSize()
                alto_calculado = (alto_orig * 240) / ancho_orig
                dibujo_foto = Image(io.BytesIO(bytes_foto), width=240, height=alto_calculado)
                nombre_foto = foto_archivo.name if hasattr(foto_archivo, 'name') else "Foto de Inspección"
                celda_foto = [dibujo_foto, Spacer(1, 3), Paragraph(f"Evidencia: {nombre_foto}", ParagraphStyle('FLabel', parent=cell_body, fontSize=7, alignment=1))]
                fila_actual.append(celda_foto)
            except:
                pass
            if len(fila_actual) == 2:
                fotos_tabla.append(fila_actual)
                fila_actual = []
        if fila_actual:
            fila_actual.append("")
            fotos_tabla.append(fila_actual)
        if fotos_tabla:
            t_fotos = Table(fotos_tabla, colWidths=[270, 270])
            t_fotos.setStyle(TableStyle([('ALIGN', (0,0), (-1,-1), 'CENTER'), ('VALIGN', (0,0), (-1,-1), 'MIDDLE'), ('PADDING', (0,0), (-1,-1), 8)]))
            story.append(t_fotos)
    
    story.append(Spacer(1, 15))
    story.append(Paragraph("4. Dictamen Final Evaluativo y Responsabilidad", subtitle_style))
    concl_data = [
        [Paragraph(f"<b>VEREDICTO TÉCNICO:</b> {dictamen}", ParagraphStyle('FD', parent=cell_body, fontSize=10))],
        [Paragraph(f"<b>Inspector Certificador:</b> {inspector}", ParagraphStyle('FI', parent=cell_body, fontSize=9))],
        [Paragraph("<i>Este reporte técnico posee carácter de declaración legal y confidencial conforme ISO 17020.</i>", ParagraphStyle('FN', parent=cell_body, fontSize=7.5))]
    ]
    t_concl = Table(concl_data, colWidths=[540])
    t_concl.setStyle(TableStyle([('BOX', (0,0), (-1,-1), 1.5, colors.HexColor('#0D1B2A')), ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#F4F6F9')), ('PADDING', (0,0), (-1,-1), 6)]))
    story.append(t_concl)
    
    doc.build(story)
    buffer.seek(0)
    return buffer


def generar_pdf_certificado_gpa(datos_cabecera, datos_equipo, id_reporte, dictamen, inspector, URL_LOGO):
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter, rightMargin=50, leftMargin=50, topMargin=50, bottomMargin=50)
    story = []
    styles = getSampleStyleSheet()
    cert_title = ParagraphStyle('GPA_CertTitle', parent=styles['Heading1'], fontSize=20, leading=24, alignment=1, textColor=colors.HexColor('#0D1B2A'))
    cert_body = ParagraphStyle('GPA_CertBody', parent=styles['BodyText'], fontSize=11, leading=19, alignment=4)
    
    try:
        req = urllib.request.Request(URL_LOGO, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req) as response:
            img_data = response.read()
        logo_cert = Image(io.BytesIO(img_data), width=100, height=62)
        logo_cert.hAlign = 'CENTER'
        story.append(logo_cert)
    except:
        pass
        
    story.append(Spacer(1, 15))
    story.append(Paragraph("<b>CERTIFICADO DE CONFORMIDAD NORMATIVA</b>", cert_title))
    story.append(Paragraph(f"<b>Certificado N°:</b> CERT-GPA-{id_reporte}", ParagraphStyle('S', alignment=1, fontSize=11, textColor=colors.HexColor('#1A3A5C'))))
    story.append(Spacer(1, 20))
    
    texto = f"El Organismo de Inspección Técnica de <b>ANDES Ingeniería y Servicios</b> certifica bajo los lineamientos operativos de la norma de seguridad <b>ASME B30.22</b> que se evaluó físicamente la siguiente unidad estructural y mecánica:"
    story.append(Paragraph(texto, cert_body))
    story.append(Spacer(1, 15))
    
    eq_info = [
        [Paragraph("<b>Cliente / Operador:</b>", cert_body), Paragraph(datos_cabecera['Cliente'], cert_body)],
        [Paragraph("<b>Tipo de Equipo:</b>", cert_body), Paragraph("Grúa de Pluma Articulada (Módulo GPA)", cert_body)],
        [Paragraph("<b>Marca / Modelo Grúa:</b>", cert_body), Paragraph(f"{datos_equipo['Marca']} / {datos_equipo['Modelo']}", cert_body)],
        [Paragraph("<b>N° Serie de Unidad:</b>", cert_body), Paragraph(datos_equipo['Serie'], cert_body)],
        [Paragraph("<b>Chasis Vehículo (Patente):</b>", cert_body), Paragraph(datos_equipo['Patente'], cert_body)]
    ]
    t_eq = Table(eq_info, colWidths=[180, 290])
    t_eq.setStyle(TableStyle([
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#1A3A5C')), ('PADDING', (0,0), (-1,-1), 7),
        ('BACKGROUND', (0,0), (0,-1), colors.HexColor('#F4F6F9')), ('BOX', (0,0), (-1,-1), 1.5, colors.HexColor('#0D1B2A'))
    ]))
    story.append(t_eq)
    
    story.append(Spacer(1, 20))
    texto_dictamen = f"Resultando conforme ante todas las pautas de ensayos de seguridad, fugas y estabilidad, se otorga el estatus definitivo de: <b><font color='#38A169'>{dictamen}</font></b>."
    story.append(Paragraph(texto_dictamen, cert_body))
    
    story.append(Spacer(1, 10))
    story.append(Paragraph(f"<b>Fecha de Inspección:</b> {datos_cabecera['Fecha']}<br/><b>Vigencia Técnica:</b> 12 Meses calendario.", cert_body))
    story.append(Spacer(1, 40))
    story.append(Paragraph(f"_______________________________________<br/><b>{inspector}</b><br/>Inspector Técnico Autorizado<br/><b>ANDES Ingeniería y Servicios</b>", ParagraphStyle('F', alignment=1, fontSize=10, leading=14)))
    
    doc.build(story)
    buffer.seek(0)
    return buffer


# --- INTERFAZ DE PANTALLA PRINCIPAL ---
def desplegar_modulo_pluma_articulada(URL_LOGO):
    st.markdown("---")
    st.caption("Plataforma de Captura de Datos en Campo — Módulo: Grúas de Pluma Articulada (GPA)")

    with st.form("formulario_checklist_gpa"):
        st.header("📋 1. Datos Generales de la Inspección")
        col1, col2 = st.columns(2)
        with col1:
            fecha = st.date_input("Fecha de inspección:", datetime.date.today(), key="gpa_f")
            cliente = st.text_input("Cliente:", key="gpa_cl")
            ubicacion = st.text_input("Ubicación / Planta:", key="gpa_ub")
        with col2:
            lugar_inspeccion = st.text_input("Lugar de inspección:", key="gpa_lug")

        st.markdown("---")
        st.header("🚜 2. Identificación del Equipo")
        col3, col4 = st.columns(2)
        with col3:
            marca = st.text_input("Marca de Grúa:", key="gpa_ma")
            modelo = st.text_input("Modelo de Grúa:", key="gpa_mo")
            serie = st.text_input("N° de Serie Grúa:", key="gpa_se")
        with col4:
            anio_fab = st.text_input("Año de Fabricación:", key="gpa_an")
            interno = st.text_input("Código Interno:", key="gpa_int")
            patente = st.text_input("Patente del Camión:", key="gpa_pat")

        st.markdown("---")
        st.header("⚙️ 3. Características Técnicas")
        col5, col6 = st.columns(2)
        with col5:
            capacidad = st.text_input("Capacidad Máxima de Carga (Ej: 12 Ton):", key="gpa_cap")
            alcance = st.text_input("Alcance Máximo Horizontal (Ej: 14.5 m):", key="gpa_alc")
        with col6:
            estabilizadores = st.text_input("Cantidad de Gatos Estabilizadores:", key="gpa_est")

        st.markdown("---")
        st.subheader("⚖️ Declaración Jurada de Independencia")
        imparcialidad = st.checkbox("Declaro formalmente bajo juramento el cumplimiento estricto de los requisitos de imparcialidad conforme ISO/IEC 17020.", key="gpa_imp_chk")

        st.markdown("---")
        st.header("🔍 4. Inspección de Requisitos Técnicos (ASME B30.22)")
        st.info("Valore individualmente cada componente e incorpore observaciones detalladas en caso de no conformidades.")

        respuestas_inspector = {}

        # Mapeo estructurado imprimiendo leyendas completas en pantalla y PDF
        for categoria, sub_items in estructura_checklist_gpa.items():
            st.markdown(f"### 📍 {categoria}")
            respuestas_inspector[categoria] = {}
            
            for sub_item in sub_items:
                partes = sub_item.split(":", 1)
                codigo_titulo = partes[0]
                descripcion_norma = partes[1] if len(partes) > 1 else ""
                
                st.markdown(f"**{codigo_titulo}** — *{descripcion_norma.strip()}*")
                c_rad, c_obs = st.columns([1, 2])
                with c_rad:
                    estado = st.radio("Dictamen:", ["Cumple", "No Cumple", "No Aplica"], key=f"r_gpa_{sub_item}", horizontal=True, label_visibility="collapsed")
                with c_obs:
                    obs = st.text_input("Observaciones:", key=f"o_gpa_{sub_item}", placeholder="Registrar desviación técnica...", label_visibility="collapsed")
                
                respuestas_inspector[categoria][codigo_titulo] = {"Resultado": estado, "Observaciones": obs}
            st.markdown("<br>", unsafe_allow_html=True)

        st.markdown("---")
        st.header("📸 5. Archivos Fotográficos")
        fotos_cargadas = st.file_uploader(
            "Cargue las capturas tomadas en campo (Placas identificatorias, componentes críticos o fallas encontradas):",
            type=["png", "jpg", "jpeg"], accept_multiple_files=True, key="fotos_gpa_uploader"
        )

        st.markdown("---")
        st.header("🏁 6. Cierre de Inspección")
        dictamen_final = st.selectbox("Estatus Final de la Unidad:", ["APROBADO", "RECHAZADO", "APROBADO CONDICIONAL"], key="gpa_dict_sel")
        inspector_firma = st.text_input("Nombre y Firma Digital del Inspector Evaluador:", key="gpa_firm_txt")

        guardar_reporte = st.form_submit_button("🔒 Registrar Reporte Oficial de Pluma Articulada")

        if guardar_reporte:
            if not cliente or not serie or not inspector_firma:
                st.error("⚠️ Validación Errónea: Los campos 'Cliente', 'N° de Serie' y 'Firma del Inspector' no pueden guardarse vacíos.")
            elif not imparcialidad:
                st.error("❌ Bloqueo Operativo: Debe firmar la declaración de imparcialidad obligatoria exigida por la norma ISO 17020.")
            else:
                id_reporte = f"GPA-{fecha.strftime('%Y%m%d')}-{random.randint(1000, 9999)}"
                
                cabecera = {"Fecha": str(fecha), "Cliente": cliente, "Ubicación": ubicacion, "Lugar": lugar_inspeccion}
                equipo = {"Marca": marca, "Modelo": modelo, "Serie": serie, "Año": anio_fab, "Interno": interno, "Patente": patente}
                tecnicos = {"Capacidad": capacidad, "Alcance": alcance, "Estabilizadores": estabilizadores}
                
                st.session_state.current_report_gpa = {
                    "id": id_reporte, "cabecera": cabecera, "equipo": equipo, "tecnicos": tecnicos,
                    "respuestas": respuestas_inspector, "dictamen": dictamen_final, "inspector": inspector_firma,
                    "fotos": fotos_cargadas if fotos_cargadas else []
                }
                
                st.session_state.historial_inspecciones.append({
                    "Informe N°": id_reporte, "Fecha": str(fecha), "Cliente": cliente, "Equipo (Serie)": serie, "Dictamen": dictamen_final, "Inspector": inspector_firma
                })
                st.success(f"✅ ¡Inspección registrada con éxito bajo el registro de control **{id_reporte}**!")

    # Bloque de procesamiento de descargas seguro fuera del form
    if 'current_report_gpa' in st.session_state:
        st.markdown("---")
        st.header("📥 Descarga de Certificados e Informes Emitidos")
        rep = st.session_state.current_report_gpa
        
        pdf_informe = generar_pdf_informe_gpa(rep['cabecera'], rep['equipo'], rep['tecnicos'], rep['respuestas'], rep['id'], rep['dictamen'], rep['inspector'], rep['fotos'], URL_LOGO)
        pdf_certificado = generar_pdf_certificado_gpa(rep['cabecera'], rep['equipo'], rep['id'], rep['dictamen'], rep['inspector'], URL_LOGO)
        
        col_d1, col_d2 = st.columns(2)
        with col_d1:
            st.download_button(
                label="📄 Descargar Informe Técnico GPA Completo (PDF)", data=pdf_informe,
                file_name=f"Informe_Tecnico_GPA_{rep['id']}.pdf", mime="application/pdf", key="btn_gpa_inf"
            )
        with col_d2:
            if rep['dictamen'] == "APROBADO":
                st.download_button(
                    label="📜 Descargar Certificado de Aprobación GPA (PDF)", data=pdf_certificado,
                    file_name=f"Certificado_Aprobacion_GPA_{rep['id']}.pdf", mime="application/pdf", key="btn_gpa_cert"
                )
            else:
                st.warning("⚠️ Certificado bloqueado debido a que la unidad se encuentra bajo estatus 'RECHAZADO' o 'CONDICIONAL'.")
