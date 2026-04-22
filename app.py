import streamlit as st
import requests
from pypdf import PdfReader
import os

st.set_page_config(page_title="Asistente HNRG", page_icon="🏥")
st.title("🏥 Asistente de Enfermería")

# 1. Recuperar clave de Secrets
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

consulta = st.text_input("¿Qué duda técnica tenés?")

if st.button("Consultar Protocolos"):
    if not api_key:
        st.error("Falta la clave API en los Secrets de Streamlit.")
    elif consulta:
        with st.spinner("Conectando con Google AI..."):
            try:
                contexto = extraer_texto()
                # LA URL QUE NO FALLA: v1beta + gemini-pro
                url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent?key={api_key}"
                
                payload = {
                    "contents": [{
                        "parts": [{"text": f"Sos un enfermero experto del HNRG. Basándote en: {contexto}\n\nPregunta: {consulta}"}]
                    }]
                }
                
                response = requests.post(url, json=payload)
                data = response.json()
                
                if response.status_code == 200:
                    st.success("✅ ¡Por fin! Conexión establecida.")
                    st.write(data['candidates'][0]['content']['parts'][0]['text'])
                else:
                    # Si esto da error, leemos el mensaje real
                    error_msg = data.get('error', {}).get('message', 'Error desconocido')
                    st.error(f"Nota del servidor: {error_msg}")
            except Exception as e:
                st.error(f"Error de red: {e}")
