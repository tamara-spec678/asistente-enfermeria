import streamlit as st
import google.generativeai as genai
from pypdf import PdfReader
import os

# Configuración de página
st.set_page_config(page_title="Asistente HNRG", page_icon="🏥")
st.title("🏥 Asistente de Enfermería")

# 1. Configuración de la API (Forma más simple posible)
if "GOOGLE_API_KEY" in st.secrets:
    genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])
else:
    st.error("Falta la clave API en los Secrets.")

def extraer_texto():
    texto_total = ""
    archivos = ["Guía de Administración de drogas HNRG 2023 (5) (1).pdf", "292+-+300+Seguridad+del+paciente.pdf"]
    for arc in archivos:
        if os.path.exists(arc):
            try:
                reader = PdfReader(arc)
                for page in reader.pages:
                    texto_total += (page.extract_text() or "") + "\n"
            except: pass
    return texto_total

consulta = st.text_input("¿Qué consulta técnica tenés?")

if st.button("Consultar"):
    if consulta:
        with st.spinner("Buscando..."):
            try:
                contexto = extraer_texto()
                # CAMBIO CLAVE: Usamos 'gemini-pro' que es el más compatible
                model = genai.GenerativeModel('gemini-pro')
                
                prompt = f"Actuá como enfermero del HNRG. Usá este texto: {contexto}\n\nPregunta: {consulta}"
                
                response = model.generate_content(prompt)
                st.success("Respuesta:")
                st.write(response.text)
            except Exception as e:
                # Esto nos va a decir exactamente qué versión está fallando ahora
                st.error(f"Error: {e}")
