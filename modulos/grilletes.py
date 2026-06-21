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

# --- ESTRUCTURA MAESTRA DEL CHECKLIST (ASME B30.26 - GRILLETES) ---
estructura_checklist_gr = {
    "A. Documentación e Información Técnica": [
        "A. Doc.1. Identificación del Fabricante: Marca del fabricante o marca comercial grabada en relieve o estampada en el cuerpo (Sec. 26-1.1.1).",
        "A. Doc.2. Capacidad Nominal (WLL): Tamaño del grillete y/o la capacidad nominal (WLL) claramente legibles en el cuerpo."
    ],
    "B. Componentes Estructurales y Alteraciones": [
        "B. Est.3. Deformación Estructural: Ausencia de dobleces, torceduras o curvaturas visibles en el cuerpo (arco) o en el perno.",
        "B. Est.4. Daño Térmico y Alteraciones: Sin evidencia de salpicaduras de soldadura, marcas de arco eléctrico o modificaciones no autorizadas (Sec. 26-1.8.1).",
        "B. Est.5. Estado de la Rosca del Perno: Rosca del perno y del cuerpo sin daños, mellas, deformaciones ni acumulación de suciedad que impida el roscado completo a mano."
    ],
    "E. Inspección Dimensional y de Desgaste (Izaje)": [
        "E. Iza.6. Control de Desgaste (Cuerpo): El desgaste en el arco del grillete no debe exceder el 10% de su dimensión original (Sec. 26-1.8.1).",
        "E. Iza.7. Control de Desgaste (Perno): El perno no debe presentar un desgaste mayor al 10% de su diámetro original. Sin juego excesivo en el acoplamiento.",
        "E. Iza.8. Fisuras y Corrosión: Ausencia de fisuras, grietas o picaduras severas por corrosión. Verificar visualmente las zonas de mayor concentración de esfuerzo."
    ],
    "G. Ensamble y Ajuste Operacional": [
        "G. Pru.9. Ensamble y Ajuste Operacional: El perno debe asentarse completamente. En grilletes de perno y tuerca, el pasador de chaveta (cotter pin) debe estar presente y expandido."
    ]
}

# --- MOTORES DE GENERACIÓN DE RENDERS PDF PARA GRILLETES ---
def generar_pdf_informe_gr(datos_cabecera, datos_equipo, respuestas, id_reporte, dictamen, inspector, lista_fotos, URL_LOGO):
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter, rightMargin=36, leftMargin=36, topMargin=36, bottomMargin=36)
    story = []
    
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle('GR_Title', parent=styles['Heading1'], fontSize=15, leading=18, textColor=colors.HexColor('#0D1B2A'))
    subtitle_style = ParagraphStyle('GR_SubTitle', parent=styles['Heading2'], fontSize=11, leading=15, textColor=colors.HexColor('#1A3A5C'), spaceBefore=12, spaceAfter=6)
    cell_body = ParagraphStyle('CellBodyGR', parent=styles['Normal'], fontSize=8.5, leading=12, textColor=colors.HexColor('#2D3748'))
    cell_dictamen = ParagraphStyle('CellDictGR', parent=styles['Normal'], fontSize=9, leading=12, alignment=1, textColor=colors.HexColor('#0D1B2A'))
    header_cell = ParagraphStyle('HeaderCellGR', parent=styles['Normal'], fontSize=9, leading=12, alignment=1, textColor=colors.white)
    cat_cell_style = ParagraphStyle('CatCellGR', parent=styles['Normal'], fontSize=9, leading=12, textColor=colors.HexColor('#0D1B2A'))

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
        <font size=10 color='#0D1B2A'>INFORME TÉCNICO DE INSPECCIÓN — ACCESORIOS DE IZAJE: GRILLETES (ASME B30.26)</font>
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
    
    story.append(Paragraph("1. Identificación y Especificaciones del Componente", subtitle_style))
    equipo_data = [
        [Paragraph(f"<b>Tipo de Grillete:</b> {datos_equipo['Tipo']}", cell_body), Paragraph(f"<b>Marca / Fabricante:</b> {datos_equipo['Marca']}", cell_body), Paragraph(f"<b>Código Trazabilidad / ID:</b> {datos_equipo['ID']}", cell_body)],
        [Paragraph(f"<b>Capacidad Nominal (WLL):</b> {datos_equipo['WLL']}", cell_body), Paragraph(f"<b>Diámetro Nominal:</b> {datos_equipo['Diametro']}", cell_body), Paragraph(f"<b>Material / Grado:</b> {datos_equipo['Grado']}", cell_body)]
    ]
    t_eq = Table(equipo_data, colWidths=[180, 180, 180])
    t_eq.setStyle(TableStyle([
        ('BOX', (0,0), (-1,-1), 1, colors.HexColor('#1A3A5C')), ('INNERGRID', (0,0), (-1,-1), 0.5, colors.HexColor('#F4F6F9')), ('PADDING', (0,0), (-1,-1), 5)
    ]))
    story.append(t_eq)
    
    story.append(Paragraph("2. Evaluación Técnica según ASME B30.26 Capítulo 26-1", subtitle_style))
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
        story.append(Paragraph("3. Registro Fotográfico de Campo (Evidencia Objetiva)", subtitle_style))
        fotos_tabla = []
        fila_actual = []
        for foto_archivo in lista_fotos:
            try:
                bytes_foto = foto_archivo.getvalue() if hasattr(foto_archivo, 'getvalue') else foto_archivo
                img_reader = ImageReader(io.BytesIO(bytes_foto))
                ancho_orig, alto_orig = img_reader.getSize()
                alto_calculado = (alto_orig * 240) / ancho_orig
                dibujo_foto = Image(io.BytesIO(bytes_foto), width=240, height=alto_calculado)
                nombre_foto = foto_archivo.name if hasattr(foto_archivo, 'name') else "Foto Grillete"
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
        [Paragraph("<i>Este reporte técnico posee carácter de declaración confidencial conforme a los lineamientos ISO 17020.</i>", ParagraphStyle('FN', parent=cell_body, fontSize=7.5))]
    ]
    t_concl = Table(concl_data, colWidths=[540])
    t_concl.setStyle(TableStyle([('BOX', (0,0), (-1,-1), 1.5, colors.HexColor('#0D1B2A')), ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#F4F6F9')), ('PADDING', (0,0), (-1,-1), 6)]))
    story.append(t_concl)
    
    doc.build(story)
    buffer.seek(0)
    return buffer


def generar_pdf_certificado_gr(datos_cabecera, datos_equipo, id_reporte, dictamen, inspector, URL_LOGO):
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter, rightMargin=50, leftMargin=50, topMargin=50, bottomMargin=50)
    story = []
    styles = getSampleStyleSheet()
    cert_title = ParagraphStyle('GR_CertTitle', parent=styles['Heading1'], fontSize=20, leading=24, alignment=1, textColor=colors.HexColor('#0D1B2A'))
    cert_body = ParagraphStyle('GR_CertBody', parent=styles['BodyText'], fontSize=11, leading=19, alignment=4)
    
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
    story.append(Paragraph(f"<b>Certificado N°:</b> CERT-GR-{id_reporte}", ParagraphStyle('S', alignment=1, fontSize=11, textColor=colors.HexColor('#1A3A5C'))))
    story.append(Spacer(1, 20))
    
    texto = f"El Organismo de Inspección Técnica de <b>ANDES Ingeniería y Servicios</b> certifica bajo los lineamientos operativos de la norma de seguridad de accesorios de izaje <b>ASME B30.26</b> que se evaluó físicamente el siguiente ítem:"
    story.append(Paragraph(texto, cert_body))
    story.append(Spacer(1, 15))
    
    eq_info = [
        [Paragraph("<b>Cliente / Solicitante:</b>", cert_body), Paragraph(datos_cabecera['Cliente'], cert_body)],
        [Paragraph("<b>Tipo de Accesorio:</b>", cert_body), Paragraph(f"Grillete - {datos_equipo['Tipo']}", cert_body)],
        [Paragraph("<b>Marca / Fabricante:</b>", cert_body), Paragraph(datos_equipo['Marca'], cert_body)],
        [Paragraph("<b>Código ID / Trazabilidad:</b>", cert_body), Paragraph(datos_equipo['ID'], cert_body)],
        [Paragraph("<b>Capacidad Nominal (WLL) / Diámetro:</b>", cert_body), Paragraph(f"{datos_equipo['WLL']} / {datos_equipo['Diametro']}", cert_body)]
    ]
    t_eq = Table(eq_info, colWidths=[180, 290])
    t_eq.setStyle(TableStyle([
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#1A3A5C')), ('PADDING', (0,0), (-1,-1), 7),
        ('BACKGROUND', (0,0), (0,-1), colors.HexColor('#F4F6F9')), ('BOX', (0,0), (-1,-1), 1.5, colors.HexColor('#0D1B2A'))
    ]))
    story.append(t_eq)
    
    story.append(Spacer(1, 20))
    texto_dictamen = f"Habiéndose completado los controles visuales, de desgaste dimensional y ajuste operacional de pernos, el veredicto definitivo del componente es: <b><font color='#38A169'>{dictamen}</font></b>."
    story.append(Paragraph(texto_dictamen, cert_body))
    
    story.append(Spacer(1, 10))
    story.append(Paragraph(f"<b>Fecha de Inspección:</b> {datos_cabecera['Fecha']}<br/><b>Vigencia Técnica Sugerida:</b> 12 Meses calendario.", cert_body))
    story.append(Spacer(1, 40))
    story.append(Paragraph(f"_______________________________________<br/><b>{inspector}</b><br/>Inspector Técnico Autorizado<br/><b>ANDES Ingeniería y Servicios</b>", ParagraphStyle('F', alignment=1, fontSize=10, leading=14)))
    
    doc.build(story)
    buffer.seek(0)
    return buffer


# --- INTERFAZ DEL SUBMÓDULO DE GRILLETES ---
def desplegar_modulo_grilletes(URL_LOGO):
    st.markdown("---")
    st.caption("Plataforma de Captura de Datos en Campo — Módulo: Grilletes (GR)")

    with st.form("formulario_checklist_gr"):
        st.header("📋 1. Datos Generales de la Inspección")
        col1, col2 = st.columns(2)
        with col1:
            fecha = st.date_input("Fecha de inspección:", datetime.date.today(), key="gr_f")
            cliente = st.text_input("Cliente:", key="gr_cl")
            ubicacion = st.text_input("Ubicación / Planta:", key="gr_ub")
        with col2:
            lugar_inspeccion = st.text_input("Lugar de inspección:", key="gr_lug")

        st.markdown("---")
        st.header("⚙️ 2. Identificación e Información Técnica del Grillete")
        col3, col4 = st.columns(2)
        with col3:
            tipo_grillete = st.selectbox("Tipo de Grillete:", ["Grillete Lira con Perno Roscado", "Grillete Lira con Perno, Tuerca y Chaveta", "Grillete Recto con Perno Roscado", "Grillete Recto con Perno, Tuerca y Chaveta", "Otro / Especial"], key="gr_ti")
            marca = st.text_input("Marca / Fabricante (Ej: Crosby, Green Pin):", key="gr_ma")
            id_trazabilidad = st.text_input("Código de Identificación / Trazabilidad (ID Interno):", key="gr_id")
        with col4:
            wll_capacidad = st.text_input("Capacidad Nominal (WLL - Ej: 4.75 Ton):", key="gr_wll")
            diametro_nominal = st.text_input("Diámetro Nominal de Arco / Perno (Ej: 3/4\"):", key="gr_di")
            grado_material = st.text_input("Grado de Material / Tipo de Acero (Ej: Grado 80, Carbono):", key="gr_gr")

        st.markdown("---")
        st.subheader("⚖️ Declaración de Imparcialidad")
        imparcialidad = st.checkbox("Declaro formalmente bajo juramento el cumplimiento estricto de los requisitos de imparcialidad e integridad técnica conforme ISO/IEC 17020.", key="gr_imp_chk")

        st.markdown("---")
        st.header("🔍 3. Inspección de Requisitos Técnicos (ASME B30.26)")
        st.info("Valore individualmente cada componente de acuerdo con los criterios de aceptación y rechazo.")

        respuestas_inspector = {}

        # Mapeo dinámico imprimiendo leyendas completas en pantalla y PDF
        for categoria, sub_items in estructura_checklist_gr.items():
            st.markdown(f"### 📍 {categoria}")
            respuestas_inspector[categoria] = {}
            
            for sub_item in sub_items:
                partes = sub_item.split(":", 1)
                codigo_titulo = partes[0]
                descripcion_norma = partes[1] if len(partes) > 1 else ""
                
                st.markdown(f"**{codigo_titulo}** — *{descripcion_norma.strip()}*")
                c_rad, c_obs = st.columns([1, 2])
                with c_rad:
                    estado = st.radio("Dictamen:", ["Cumple", "No Cumple", "No Aplica"], key=f"r_gr_{sub_item}", horizontal=True, label_visibility="collapsed")
                with c_obs:
                    obs = st.text_input("Observaciones:", key=f"o_gr_{sub_item}", placeholder="Registrar hallazgo si aplica...", label_visibility="collapsed")
                
                respuestas_inspector[categoria][codigo_titulo] = {"Resultado": estado, "Observaciones": obs}
            st.markdown("<br>", unsafe_allow_html=True)

        st.markdown("---")
        st.header("📸 4. Registro Fotográfico de Evidencias")
        fotos_cargadas = st.file_uploader(
            "Cargue capturas nítidas del grillete (Marcas grabadas, rosca, cuerpo completo o fallas puntuales):",
            type=["png", "jpg", "jpeg"], accept_multiple_files=True, key="fotos_gr_uploader"
        )

        st.markdown("---")
        st.header("🏁 5. Dictamen Oficial del Organismo")
        dictamen_final = st.selectbox("Estatus Técnico Final del Grillete:", ["APROBADO", "RECHAZADO"], key="gr_dict_sel")
        inspector_firma = st.text_input("Nombre y Firma Digital del Inspector Evaluador Autorizado:", key="gr_firm_txt")

        guardar_reporte = st.form_submit_button("🔒 Registrar Reporte Oficial de Grillete")

        if guardar_reporte:
            if not cliente or not id_trazabilidad or not inspector_firma:
                st.error("⚠️ Error de Datos: Los campos 'Cliente', 'Código de Identificación / ID' y 'Firma del Inspector' son de llenado obligatorio.")
            elif not imparcialidad:
                st.error("❌ Bloqueo Normativo: Debe firmar la declaración jurada de imparcialidad técnica exigida por la norma ISO 17020.")
            else:
                id_reporte = f"GR-{fecha.strftime('%Y%m%d')}-{random.randint(1000, 9999)}"
                
                cabecera = {"Fecha": str(fecha), "Cliente": cliente, "Ubicación": ubicacion, "Lugar": lugar_inspeccion}
                equipo = {"Tipo": tipo_grillete, "Marca": marca, "ID": id_trazabilidad, "WLL": wll_capacidad, "Diametro": diametro_nominal, "Grado": grado_material}
                
                st.session_state.current_report_gr = {
                    "id": id_reporte, "cabecera": cabecera, "equipo": equipo,
                    "respuestas": respuestas_inspector, "dictamen": dictamen_final, "inspector": inspector_firma,
                    "fotos": fotos_cargadas if fotos_cargadas else []
                }
                
                st.session_state.historial_inspecciones.append({
                    "Informe N°": id_reporte, "Fecha": str(fecha), "Cliente": cliente, "Equipo (Serie)": id_trazabilidad, "Dictamen": dictamen_final, "Inspector": inspector_firma
                })
                st.success(f"✅ ¡Inspección de Grillete guardada exitosamente bajo el registro **{id_reporte}**!")

    # Descargas independientes fuera del formulario
    if 'current_report_gr' in st.session_state:
        st.markdown("---")
        st.header("📥 Descarga de Certificados e Informes Emitidos")
        rep = st.session_state.current_report_gr
        
        pdf_informe = generar_pdf_informe_gr(rep['cabecera'], rep['equipo'], rep['respuestas'], rep['id'], rep['dictamen'], rep['inspector'], rep['fotos'], URL_LOGO)
        pdf_certificado = generar_pdf_certificado_gr(rep['cabecera'], rep['equipo'], rep['id'], rep['dictamen'], rep['inspector'], URL_LOGO)
        
        col_d1, col_d2 = st.columns(2)
        with col_d1:
            st.download_button(
                label="📄 Descargar Informe Técnico Grillete (PDF)", data=pdf_informe,
                file_name=f"Informe_Tecnico_Grillete_{rep['id']}.pdf", mime="application/pdf", key="btn_gr_inf"
            )
        with col_d2:
            if rep['dictamen'] == "APROBADO":
                st.download_button(
                    label="📜 Descargar Certificado de Aprobación Grillete (PDF)", data=pdf_certificado,
                    file_name=f"Certificado_Aprobacion_Grillete_{rep['id']}.pdf", mime="application/pdf", key="btn_gr_cert"
                )
            else:
                st.warning("⚠️ El Certificado no se emite debido a que el componente se encuentra 'RECHAZADO' ante los criterios mínimos de seguridad.")
