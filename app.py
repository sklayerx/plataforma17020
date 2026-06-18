import streamlit as st
import datetime
import random

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

    # Estructura completa extraída textualmente del documento
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

    # Diccionario general para almacenar los resultados del formulario
    respuestas_inspector = {}

    # Generación dinámica de la interfaz respetando los títulos y textos originales
    for categoria, sub_items in estructura_checklist.items():
        st.markdown(f"### 📍 {categoria}")
        
        for sub_item in sub_items:
            # Dividir el nombre corto del texto explicativo
            partes = sub_item.split(":", 1)
            titulo_item = partes[0]
            descripcion_item = partes[1] if len(partes) > 1 else ""
            
            st.markdown(f"**{titulo_item}** — *{descripcion_item.strip()}*")
            
            c_rad, c_obs = st.columns([1, 2])
            with c_rad:
                estado = st.radio(
                    "Dictamen:", 
                    ["Cumple", "No Cumple", "No Aplica"], 
                    key=f"rad_{sub_item}", 
                    horizontal=True,
                    label_visibility="collapsed"
                )
            with c_obs:
                obs = st.text_input(
                    "Observaciones:", 
                    key=f"obs_{sub_item}", 
                    placeholder="Registrar hallazgo si aplica...",
                    label_visibility="collapsed"
                )
            
            # Guardar la respuesta estructurada
            respuestas_inspector[sub_item] = {"Resultado": estado, "Observaciones": obs}
        st.markdown("<br>", unsafe_allow_html=True)

    st.markdown("---")
    
    # === SECCIÓN 6: CONCLUSIÓN ===
    st.header("🏁 5. Dictamen Final del Organismo")
    dictamen_final = st.selectbox("Resultado de la Inspección (Dictamen Técnico):", ["APROBADO", "RECHAZADO", "APROBADO CONDICIONAL"])
    inspector_firma = st.text_input("Nombre y Firma Digital del Inspector Técnico Autorizado:")

    # Botón de Guardado
    guardar_reporte = st.form_submit_button("🔒 Registrar Reporte de Inspección Oficial")

    if guardar_reporte:
        if not cliente or not serie or not inspector_firma:
            st.error("⚠️ Error de Integridad: Los campos 'Cliente', 'Serie del Equipo' y 'Firma del Inspector' son de llenado obligatorio para mantener la trazabilidad.")
        elif not imparcialidad:
            st.error("❌ Bloqueo Normativo: No se puede generar un informe sin la declaración jurada de imparcialidad (ISO 17020 Cláusula 4.1).")
        else:
            # Generar número de reporte único e inalterable (Requisito 7.4)
            id_reporte = f"INF-GM-{fecha.strftime('%Y%m%d')}-{random.randint(1000, 9999)}"
            
            # Crear el registro histórico para la tabla
            registro_historico = {
                "Informe N°": id_reporte,
                "Fecha": str(fecha),
                "Cliente": cliente,
                "Equipo (Serie)": serie,
                "Dictamen": dictamen_final,
                "Inspector": inspector_firma
            }
            
            st.session_state.historial_inspecciones.append(registro_historico)
            st.success(f"✅ ¡Inspección guardada exitosamente en el registro! Código Único: **{id_reporte}**")

# === SECCIÓN 7: HISTORIAL DE REGISTROS (Requisito 8.4) ===
st.markdown("---")
st.header("🗄️ Historial de Informes de Grúas Móviles")

if st.session_state.historial_inspecciones:
    st.dataframe(st.session_state.historial_inspecciones, use_container_width=True)
    st.info("💡 **Nota de Auditoría:** Cada fila representa un registro de inspección inalterable. Para una fase de producción final, se recomienda enlazar este flujo a una base de datos persistente (SQL) para asegurar el almacenamiento a largo plazo.")
else:
    st.warning("No hay informes registrados en la sesión actual.")
