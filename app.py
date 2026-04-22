import streamlit as st
import google.generativeai as genai
from pypdf import PdfReader
import os

# Configuración de la página
st.set_page_config(page_title="Asistente HNRG", page_icon="🏥")
st.title("🏥 Asistente de Enfermería")

# 1. CONFIGURACIÓN SEGÚN GUÍA OFICIAL
if "GOOGLE_API_KEY" in st.secrets:
    # Forzamos la conexión a la versión 1 (estable)
    genai.configure(api_key=st.secrets["GOOGLE_API_KEY"], transport='rest')
else:
    st.error("Falta la clave API en los Secrets.")

def extraer_texto():
    texto_total = ""
    archivos = ["Guía de Administración de drogas HNRG 2023 (5) (1).pdf", "292+-+300+Seguridad+del+paciente.pdf"]
    for arc in archivos:
        if os.path.exists(arc):
            try:
                pdf = PdfReader(arc)
                for pagina in pdf.pages:
                    texto_total += (pagina.extract_text() or "") + "\n"
            except: pass
    return texto_total

consulta = st.text_input("¿Qué duda técnica tenés?")

if st.button("Consultar"):
    if consulta:
        with st.spinner("Conectando con Gemini..."):
            try:
                contexto = extraer_texto()
                # Usamos el modelo flash que es el más moderno y compatible
                model = genai.GenerativeModel('gemini-1.5-flash')
                
                # Generamos el contenido
                response = model.generate_content(
                    f"Sos un enfermero experto del HNRG. Respondé basándote en esto: {contexto}\n\nPregunta: {consulta}"
                )
                
                st.success("Respuesta:")
                st.write(response.text)
            except Exception as e:
                st.error(f"Error detectado: {e}")
                st.info("Si el error es 404, probaremos cambiar a 'gemini-1.0-pro' en el código.")
