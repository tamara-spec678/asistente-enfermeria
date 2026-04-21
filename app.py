import streamlit as st
import google.generativeai as genai
from pypdf import PdfReader
import os

# --- CONFIGURACIÓN DE NOMBRES ---
archivo_1 = "Guía de Administración de drogas HNRG 2023 (5) (1).pdf"
archivo_2 = "292+-+300+Seguridad+del+paciente.pdf"

# Configuración visual
st.set_page_config(page_title="Asistente de Enfermería", page_icon="🏥")

st.markdown("""
    <style>
    .stApp { background-color: #F0F2f6; }
    .stButton>button { width: 100%; border-radius: 20px; background-color: #007BFF; color: white; }
    </style>
    """, unsafe_allow_html=True)

st.title("🏥 Asistente de Enfermería")
st.info("Protocolos HNRG y Seguridad del Paciente")

# Configuración de API desde Secrets
if "GOOGLE_API_KEY" in st.secrets:
    genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])
else:
    st.error("Falta la clave API en los Secrets de Streamlit.")

# Función para leer los PDFs
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

# Interfaz de usuario
pregunta = st.text_input("¿Qué duda técnica tenés?", placeholder="Ej: Dilución de fármacos...")

if st.button("Consultar Protocolos"):
    if pregunta:
        with st.spinner("Buscando en los PDFs subidos..."):
            try:
                contexto, cantidad = leer_protocolos()
                if cantidad == 0:
                    st.error("No se encontraron los archivos PDF en GitHub. Revisá que los nombres coincidan exactamente.")
                else:
                   model = genai.GenerativeModel('gemini-1.5-flash')
                    prompt = f"Sos un enfermero experto. Respondé de forma técnica usando este material: {contexto}\n\nPregunta: {pregunta}"
                    response = model.generate_content(prompt)
                    st.markdown("### 📋 Respuesta del Asistente:")
                    st.write(response.text)
            except Exception as e:
                st.error(f"Error: {e}")
    else:
        st.warning("Por favor, escribí una consulta.")
