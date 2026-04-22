import streamlit as st
import requests
from pypdf import PdfReader
import os

# Configuración de página
st.set_page_config(page_title="Asistente HNRG", page_icon="🏥")
st.title("🏥 Asistente de Enfermería")

# 1. Obtener la Clave API de los Secrets
api_key = st.secrets.get("GOOGLE_API_KEY")

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
    if not api_key:
        st.error("Falta la clave API en los Secrets.")
    elif consulta:
        with st.spinner("Conectando con el servidor central..."):
            try:
                contexto = extraer_texto()
                # CONEXIÓN DIRECTA POR HTTP (Bypass total de librerías)
                url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={api_key}"
                
                payload = {
                    "contents": [{
                        "parts": [{"text": f"Sos un enfermero experto del Hospital Gutiérrez. Respondé basándote en este texto: {contexto}\n\nPregunta: {consulta}"}]
                    }]
                }
                
                response = requests.post(url, json=payload)
                result = response.json()
                
                if response.status_code == 200:
                    respuesta_ia = result['candidates'][0]['content']['parts'][0]['text']
                    st.success("Respuesta del Asistente:")
                    st.write(respuesta_ia)
                else:
                    st.error(f"Error de Google: {result['error']['message']}")
            except Exception as e:
                st.error(f"Ocurrió un error: {e}")
