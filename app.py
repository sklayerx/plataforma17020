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
    
    # Encabezado Oficial en el PDF
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
    cert_body = ParagraphStyle('CertBody', parent=styles['BodyText'], fontSize=12, leading=20, alignment=4, spaceBefore=15
