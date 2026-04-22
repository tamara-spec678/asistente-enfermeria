import streamlit as st
import google.generativeai as genai
from pypdf import PdfReader
import os

# Configuración de la página
st.set_page_config(page_title="Asistente HNRG", page_icon="🏥")
st.title("🏥 Asistente de Enfermería")

# 1. CONFIGURACIÓN ESTABLE
if "GOOGLE_API_KEY" in st.secrets:
    # Mantenemos el transporte REST que es más seguro
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

consulta = st.text_input("¿Qué consulta técnica tenés?")

if st.button("Consultar Protocolos"):
    if consulta:
        with st.spinner("Conectando con el servidor..."):
            try:
                contexto = extraer_texto()
                
                # CAMBIO CRUCIAL: Usamos gemini-1.0-pro
                # Este modelo es el que el error 404 suele aceptar cuando Flash falla
                model = genai.GenerativeModel('gemini-1.0-pro')
                
                prompt = f"Actuá como enfermero del HNRG. Respondé basándote en: {contexto}\n\nPregunta: {consulta}"
                
                response = model.generate_content(prompt)
                
                st.success("Respuesta:")
                st.write(response.text)
            except Exception as e:
                st.error(f"Error técnico: {e}")
