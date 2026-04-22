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
                    texto += (page.extract_text() or "") + " "
            except: pass
    # Recortamos un poco el texto por si es muy largo para la API gratuita
    return texto[:30000] 

if not api_key:
    st.error("⚠️ Falta la clave API en Secrets.")
else:
    consulta = st.text_input("¿Qué consulta técnica tenés?")

    if st.button("Consultar Protocolos"):
        if consulta:
            with st.spinner("Buscando en los protocolos del hospital..."):
                try:
                    contexto = extraer_texto()
                    # Usamos el modelo más estable de los 38 que tenés
                    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={api_key}"
                    
                    payload = {
                        "contents": [{
                            "parts": [{"text": f"Sos enfermero del Hospital Gutiérrez. Usá este contexto: {contexto}\n\nPregunta: {consulta}"}]
                        }]
                    }
                    
                    response = requests.post(url, json=payload)
                    
                    # Verificamos si la respuesta no está vacía
                    if response.text:
                        data = response.json()
                        if response.status_code == 200:
                            st.success("✅ Protocolo encontrado:")
                            st.write(data['candidates'][0]['content']['parts'][0]['text'])
                        else:
                            st.error(f"Error de Google: {data.get('error', {}).get('message')}")
                    else:
                        st.error("El servidor de Google no envió datos. Intentá con una pregunta más corta.")
                        
                except Exception as e:
                    st.error(f"Error de conexión: {e}")
