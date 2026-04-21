import streamlit as st
import google.generativeai as genai
from pypdf import PdfReader
import os

# --- CONFIGURACIÓN DE TUS ARCHIVOS ---
# Asegurate de que los nombres en GitHub sean exactamente estos
archivo_1 = "Guía de Administración de drogas HNRG 2023 (5) (1).pdf"
archivo_2 = "292+-+300+Seguridad+del+paciente.pdf"

st.set_page_config(page_title="Asistente de Enfermería", page_icon="🏥")

st.title("🏥 Asistente de Enfermería")
st.info("Protocolos HNRG y Seguridad del Paciente")

# CONFIGURACIÓN DE LA IA
if "GOOGLE_API_KEY" in st.secrets:
    # Usamos la configuración estándar para las claves nuevas
    genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])
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

# Interfaz de consulta
pregunta = st.text_input("¿Qué duda técnica tenés?", placeholder="Ej: Dilución de fármacos...")

if st.button("Consultar Protocolos"):
    if pregunta:
        with st.spinner("Buscando en los protocolos del hospital..."):
            try:
                contexto, cantidad = leer_protocolos()
                if cantidad == 0:
                    st.error("No se encontraron los archivos PDF. Verificá que los hayas subido a GitHub con los nombres correctos.")
                else:
                    # USAMOS EL MODELO MÁS MODERNO
                    model = genai.GenerativeModel('gemini-1.5-flash')
                    
                    prompt = f"""
                    Sos un enfermero experto del Hospital Gutiérrez (HNRG). 
                    Respondé de forma profesional y técnica basándote SOLO en este material:
                    {contexto}
                    
                    Pregunta: {pregunta}
                    """
                    
                    response = model.generate_content(prompt)
                    st.markdown("### 📋 Respuesta Técnica:")
                    st.write(response.text)
            except Exception as e:
                st.error(f"Error de conexión o clave: {e}")
    else:
        st.warning("Por favor, escribí una consulta para poder ayudarte.")
