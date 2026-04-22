import streamlit as st
import requests
from pypdf import PdfReader
import os

st.set_page_config(page_title="Asistente HNRG", page_icon="🏥")
st.title("🏥 Asistente de Enfermería")

# 1. Recuperar clave de los Secrets
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

consulta = st.text_input("¿Qué duda técnica tenés?", placeholder="Ej: Dilución de antibióticos...")

if st.button("Consultar Protocolos"):
    if not api_key:
        st.error("Falta la clave API en los Secrets de Streamlit.")
    elif consulta:
        with st.spinner("Buscando en las guías del HNRG..."):
            try:
                contexto = extraer_texto()
                
                # LA URL DEFINITIVA (Versión 1 Estable + Gemini 1.5 Flash)
                url = f"https://generativelanguage.googleapis.com/v1/models/gemini-1.5-flash:generateContent?key={api_key}"
                
                payload = {
                    "contents": [{
                        "parts": [{"text": f"Actuá como un enfermero tutor del Hospital Gutiérrez. Basándote exclusivamente en este texto: {contexto}\n\nPregunta: {consulta}"}]
                    }]
                }
                
                response = requests.post(url, json=payload)
                data = response.json()
                
                if response.status_code == 200:
                    # Si todo sale bien, mostramos la respuesta
                    respuesta = data['candidates'][0]['content']['parts'][0]['text']
                    st.success("✅ Información encontrada:")
                    st.markdown(respuesta)
                else:
                    # Si Google da error, mostramos el mensaje real para saber qué pasa
                    msg_error = data.get('error', {}).get('message', 'Error desconocido')
                    st.error(f"Error de Google: {msg_error}")
            except Exception as e:
                st.error(f"Error de conexión: {e}")
