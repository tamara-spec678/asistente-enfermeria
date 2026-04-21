import streamlit as st
import google.generativeai as genai
from pypdf import PdfReader
import os

# --- NOMBRES DE TUS ARCHIVOS ---
archivo_1 = "Guía de Administración de drogas HNRG 2023 (5) (1).pdf"
archivo_2 = "292+-+300+Seguridad+del+paciente.pdf"

st.set_page_config(page_title="Asistente de Enfermería", page_icon="🏥")

st.title("🏥 Asistente de Enfermería")
st.info("Protocolos HNRG y Seguridad del Paciente")

# CONFIGURACIÓN DE SEGURIDAD PARA EVITAR EL ERROR 404
if "GOOGLE_API_KEY" in st.secrets:
    # Esta línea es la clave: fuerza el uso de la versión estable 'v1'
    client_options = {'api_version': 'v1'}
    genai.configure(
        api_key=st.secrets["GOOGLE_API_KEY"],
        transport='rest',
        client_options=client_options
    )
else:
    st.error("Falta la clave API en los Secrets de Streamlit.")

def leer_protocolos():
    texto = ""
    archivos_presentes = 0
    for nombre_archivo in [archivo_1, archivo_2]:
        if os.path.exists(nombre_archivo):
            try:
                reader = PdfReader(nombre_archivo)
                for page in reader.pages:
                    texto += (page.extract_text() or "") + "\n"
                archivos_presentes += 1
            except Exception as e:
                st.error(f"Error al leer {nombre_archivo}: {e}")
    return texto, archivos_presentes

pregunta = st.text_input("¿Qué duda técnica tenés?", placeholder="Ej: Dilución de fármacos...")

if st.button("Consultar Protocolos"):
    if pregunta:
        with st.spinner("Buscando en los PDFs..."):
            try:
                contexto, cantidad = leer_protocolos()
                if cantidad == 0:
                    st.error("No encontré los archivos. Verificá que los nombres en GitHub sean idénticos.")
                else:
                    # Usamos el nombre base del modelo
                    model = genai.GenerativeModel('gemini-1.5-flash')
                    response = model.generate_content(f"Sos un asistente experto. Usando este material: {contexto}\n\nPregunta: {pregunta}")
                    st.markdown("### 📋 Respuesta:")
                    st.write(response.text)
            except Exception as e:
                st.error(f"Error de conexión: {e}")
    else:
        st.warning("Por favor, escribí una consulta.")
