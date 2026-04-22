import streamlit as st
import requests
from pypdf import PdfReader
import os

st.set_page_config(page_title="Asistente HNRG", page_icon="🏥")
st.title("🏥 Asistente de Enfermería")

# 1. Recuperar clave
api_key = st.secrets.get("GOOGLE_API_KEY")

def extraer_texto():
    texto = ""
    archivos = ["Guía de Administración de drogas HNRG 2023 (5) (1).pdf", "292+-+300+Seguridad+del+paciente.pdf"]
    for arc in archivos:
        if os.path.exists(arc):
            try:
                reader = PdfReader(arc)
                for page in reader.pages:
                    texto += (page.extract_text() or "") + "\n"
            except: pass
    return texto

consulta = st.text_input("¿Qué consulta técnica tenés?")

if st.button("Consultar Protocolos"):
    if not api_key:
        st.error("Falta la clave API en Secrets.")
    elif consulta:
        with st.spinner("Conectando directamente con Google AI..."):
            try:
                contexto = extraer_texto()
                # USAMOS LA URL DIRECTA (Sin librerías intermedias)
                url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={api_key}"
                
                payload = {
                    "contents": [{
                        "parts": [{"text": f"Sos un enfermero experto del HNRG. Respondé basándote en: {contexto}\n\nPregunta: {consulta}"}]
                    }]
                }
                
                response = requests.post(url, json=payload)
                data = response.json()
                
                if response.status_code == 200:
                    st.success("¡Conexión exitosa!")
                    st.write(data['candidates'][0]['content']['parts'][0]['text'])
                else:
                    # Si esto falla, el problema es la clave API, no el código
                    st.error(f"Error de Google: {data['error']['message']}")
            except Exception as e:
                st.error(f"Error de conexión: {e}")
