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
                reader = PdfReader(arc)
                for page in reader.pages:
                    texto += (page.extract_text() or "") + "\n"
            except: pass
    return texto

consulta = st.text_input("¿Qué duda técnica tenés?")

if st.button("Consultar Protocolos"):
    if not api_key:
        st.error("Falta la clave API en Secrets.")
    elif consulta:
        with st.spinner("Accediendo a la base de datos estable..."):
            try:
                contexto = extraer_texto()
                # USAMOS EL MODELO CON NOMBRE TÉCNICO COMPLETO (La llave maestra)
                url = f"https://generativelanguage.googleapis.com/v1/models/gemini-1.0-pro-001:generateContent?key={api_key}"
                
                payload = {
                    "contents": [{
                        "parts": [{"text": f"Actuá como enfermero del HNRG. Respondé basándote en: {contexto}\n\nPregunta: {consulta}"}]
                    }]
                }
                
                response = requests.post(url, json=payload)
                data = response.json()
                
                if response.status_code == 200:
                    st.success("✅ ¡Conexión lograda!")
                    st.write(data['candidates'][0]['content']['parts'][0]['text'])
                else:
                    # Este mensaje nos dirá si la clave está activa o no
                    st.error(f"Error de Google: {data['error']['message']}")
            except Exception as e:
                st.error(f"Error de conexión: {e}")
