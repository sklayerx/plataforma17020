import streamlit as st
import datetime
import random

# Configuración de la página
st.set_page_config(page_title="Sistema de Gestión ISO/IEC 17020", layout="wide")

st.title("🛡️ Sistema de Gestión para Organismos de Inspección (ISO/IEC 17020)")
st.caption("Prototipo de Cumplimiento Normativo - Control de Inspecciones e Imparcialidad")

# Inicializar una base de datos ficticia en la sesión
if 'inspecciones' not in st.session_state:
    st.session_state.inspecciones = []

# --- PANEL LATERAL: Información del Sistema ---
st.sidebar.header("Control de Versiones y Gestión")
st.sidebar.info("""
**Código de Procedimiento:** P-INS-01  
**Versión del Software:** 1.0.0  
**Estado:** Entorno de Desarrollo (Sandbox)  
""")

# --- SECCIÓN 1: Nueva Inspección (Requisito 7.1 y 4.1 ISO 17020) ---
st.header("📋 Registro de Nueva Inspección")

with st.form("formulario_inspeccion"):
    col1, col2 = st.columns(2)
    
    with col1:
        inspector = st.text_input("Nombre del Inspector Autorizado:")
        cliente = st.text_input("Nombre del Cliente / Solicitante:")
        item_inspeccion = st.selectbox("Ítem a Inspeccionar:", [
            "Instalación Eléctrica Industrial",
            "Recipiente a Presión / Caldera",
            "Vehículo de Carga Pesada",
            "Estructura Metálica"
        ])
    
    with col2:
        fecha = st.date_input("Fecha de la Inspección", datetime.date.today())
        resultado = st.radio("Dictamen Preliminar:", ["Conforme", "No Conforme", "Pendiente de Acción Correctiva"])
    
    st.subheader("⚖️ Declaración de Imparcialidad (Requisito 4.1)")
    conflicto = st.checkbox("Declaro bajo juramento que NO poseo presiones comerciales, financieras o de otra índole, ni relación con el diseño, fabricación o mantenimiento del ítem que puedan comprometer mi juicio técnico.")

    # Botón de envío del formulario
    enviado = st.form_submit_button("Firmar y Registrar Inspección")

    if enviado:
        if not inspector or not cliente:
            st.error("⚠️ Error de Integridad: Todos los campos del personal y cliente son obligatorios.")
        elif not conflicto:
            st.error("❌ Bloqueo Normativo: No puede registrar la inspección si no acepta la declaración de imparcialidad.")
        else:
            # Generación de ID único y trazable (Requisito 7.4 - Informes de Inspección)
            id_informe = f"INF-{fecha.strftime('%Y%m%d')}-{random.randint(100, 999)}"
            
            # Guardar registro
            nueva_inspeccion = {
                "id": id_informe,
                "inspector": inspector,
                "cliente": cliente,
                "item": item_inspeccion,
                "fecha": str(fecha),
                "resultado": resultado,
                "imparcialidad_ok": "Sí" if conflicto else "No"
            }
            st.session_state.inspecciones.append(nueva_inspeccion)
            st.success(f"✅ Inspección registrada con éxito. Código de Informe Único: **{id_informe}**")

# Línea divisoria corregida para que Python no tire error
st.markdown("---")

# --- SECCIÓN 2: Control de Registros e Informes (Requisito 7.3 y 8.4) ---
st.header("🗄️ Historial de Inspecciones (Registro Inalterable en Sesión)")

if st.session_state.inspecciones:
    # Mostrar los datos en una tabla ordenada
    st.dataframe(st.session_state.inspecciones, use_container_width=True)
    
    # Simulación de auditoría
    st.info("💡 **Nota del Auditor:** Este registro digital actúa como evidencia objetiva para las auditorías de acreditación. Garantiza que cada informe emitido está vinculado a un inspector calificado y una declaración de imparcialidad.")
else:
    st.warning("No hay registros de inspección cargados en el sistema actualmente.")