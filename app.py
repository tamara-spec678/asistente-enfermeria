import streamlit as st
import requests
from pypdf import PdfReader
import os

st.set_page_config(page_title="Asistente HNRG", page_icon="🏥")
st.title("🏥 Asistente de Enfermería")

api_key = st.secrets.get("GOOGLE_API_KEY")

def extraer_texto():
    texto = ""
    archivos = ["Guía de Administración de drogas HNRG 2023 (5) (1).pdf", "292+-+300+Seguridad+del+paciente.pdf"]
    for arc in archivos:
        if os.path.exists(arc):
            try:
                pdf = PdfReader(arc)
                for page in pdf.pages:
                    texto += (page.extract_text() or "") + "\n"
            except: pass
    return texto

consulta = st.text_input("¿En qué puedo ayudarte hoy?", placeholder="Ej: Dilución de fármacos...")

if st.button("Consultar Protocolos"):
    if not api_key:
        st.error("Falta la clave API en los Secrets.")
    elif consulta:
        with st.spinner("Conectando con la base de datos del hospital..."):
            try:
                contexto = extraer_texto()
                # URL oficial estable para 2026
                url = f"https://generativelanguage.googleapis.com/v1/models/gemini-1.5-flash:generateContent?key={api_key}"
                
                payload = {
                    "contents": [{
                        "parts": [{"text": f"Sos un enfermero experto del Hospital Gutiérrez. Respondé basándote en: {contexto}\n\nPregunta: {consulta}"}]
                    }]
                }
                
                response = requests.post(url, json=payload)
                data = response.json()
                
                if response.status_code == 200:
                    st.success("✅ ¡Conexión exitosa!")
                    st.write(data['candidates'][0]['content']['parts'][0]['text'])
                else:
                    msg = data.get('error', {}).get('message', 'Error desconocido')
                    st.error(f"Aviso de Google: {msg}")
            except Exception as e:
                st.error(f"Error técnico: {e}")
