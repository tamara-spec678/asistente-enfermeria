import streamlit as st
import requests
from pypdf import PdfReader
import os

st.set_page_config(page_title="Asistente HNRG", page_icon="🏥")
st.title("🏥 Asistente de Enfermería")

# Recuperamos la clave
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

consulta = st.text_input("¿Qué duda técnica tenés?")

if st.button("Consultar"):
    if not api_key:
        st.error("Falta la clave API en los Secrets.")
    elif consulta:
        with st.spinner("Buscando en protocolos..."):
            try:
                contexto = extraer_texto()
                # Esta es la URL más básica y estable de todas
                url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={api_key}"
                
                payload = {
                    "contents": [{
                        "parts": [{"text": f"Actuá como enfermero del HNRG. Usá este texto como base: {contexto}\n\nPregunta: {consulta}"}]
                    }]
                }
                
                response = requests.post(url, json=payload)
                data = response.json()
                
                if response.status_code == 200:
                    st.success("✅ ¡Logramos la conexión!")
                    st.write(data['candidates'][0]['content']['parts'][0]['text'])
                else:
                    # Si falla, nos va a decir exactamente qué falta habilitar
                    st.error(f"Detalle del error: {data['error']['message']}")
            except Exception as e:
                st.error(f"Error inesperado: {e}")
