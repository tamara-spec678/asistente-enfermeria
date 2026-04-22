import streamlit as st
import google.generativeai as genai
from pypdf import PdfReader
import os

st.set_page_config(page_title="Asistente de Enfermería", page_icon="🏥")

st.title("Asistente de Enfermería 🏥")
st.caption("Hospital de Niños Ricardo Gutiérrez")

# Configuración de la clave con la librería oficial
api_key = st.secrets.get("GOOGLE_API_KEY")
if api_key:
    genai.configure(api_key=api_key)

@st.cache_data(ttl=3600)
def cargar_manuales():
    texto_total = ""
    archivos = [f for f in os.listdir('.') if f.lower().endswith('.pdf')]
    for archivo in archivos:
        try:
            reader = PdfReader(archivo)
            # Solo leemos texto, sin vueltas
            for page in reader.pages:
                t = page.extract_text()
                if t: texto_total += t + " "
        except: pass
    # Un límite seguro para no "romper" la clave gratis
    return texto_total[:30000]

if not api_key:
    st.error("Configurá la API Key en los Secrets.")
else:
    contexto_manual = cargar_manuales()
    
    consulta = st.text_input("¿Qué duda técnica tenés?")

    if st.button("Consultar"):
        if consulta and contexto_manual:
            with st.spinner("Buscando en protocolos..."):
                try:
                    # Usamos la conexión oficial (más estable)
                    model = genai.GenerativeModel('gemini-1.5-flash')
                    
                    prompt = (
                        f"Actuá como un asistente de enfermería del Hospital Gutiérrez. "
                        f"Basate en este texto: {contexto_manual}. "
                        f"Responde de forma concisa: {consulta}"
                    )
                    
                    response = model.generate_content(prompt)
                    
                    if response.text:
                        st.info(response.text)
                    else:
                        st.warning("No se obtuvo respuesta. Intentá nuevamente.")
                
                except Exception as e:
                    if "429" in str(e):
                        st.error("⚠️ Límite de Google alcanzado. Por favor, esperá 60 segundos literales sin tocar nada y probá de nuevo.")
                    else:
                        st.error(f"Error técnico: {e}")

st.sidebar.caption("Versión con Conector Oficial de Google")
