import streamlit as st
import requests
from pypdf import PdfReader
import os

st.set_page_config(page_title="Asistente de Enfermería", page_icon="🏥")

st.title("Asistente de Enfermería 🏥")
st.caption("Hospital de Niños Ricardo Gutiérrez")

api_key = st.secrets.get("GOOGLE_API_KEY")

@st.cache_data(ttl=3600)
def buscar_en_manuales(consulta_palabra):
    texto_hallado = ""
    archivos = [f for f in os.listdir('.') if f.lower().endswith('.pdf')]
    
    for archivo in archivos:
        try:
            reader = PdfReader(archivo)
            for page in reader.pages:
                content = page.extract_text()
                if content and consulta_palabra.lower() in content.lower():
                    texto_hallado += content + " "
                    if len(texto_hallado) > 20000: break # Seguridad para no saturar
        except: pass
    return texto_hallado[:25000]

if not api_key:
    st.error("Falta la API Key.")
else:
    consulta = st.text_input("Ingresá tu duda técnica (ej: Dipirona):")

    if st.button("Consultar"):
        if consulta:
            with st.spinner("Buscando en protocolos..."):
                # Filtramos el texto antes de mandarlo a la IA
                palabra_clave = consulta.split()[0]
                contexto = buscar_en_manuales(palabra_clave)
                
                try:
                    # USAMOS EL MODELO FLASH QUE ES MÁS TOLERANTE CON LA CLAVE GRATUITA
                    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={api_key}"
                    
                    payload = {
                        "contents": [{
                            "parts": [{
                                "text": f"Contexto de los manuales del hospital: {contexto}\n\nPregunta: {consulta}\n\nResponde de forma técnica y breve."
                            }]
                        }]
                    }
                    
                    response = requests.post(url, json=payload)
                    data = response.json()
                    
                    if "candidates" in data:
                        res = data["candidates"][0]["content"]["parts"][0]["text"]
                        st.markdown(f"**Respuesta:**")
                        st.success(res)
                    else:
                        # Si falla, le avisamos al usuario que espere un poquito
                        st.error("Google está procesando muchas consultas. Esperá 30 segundos y volvé a presionar el botón.")
                except:
                    st.error("Error de conexión. Reintentá.")

st.sidebar.info("Consejo: Si da error, esperá 30 segundos. Es el límite de la versión gratuita de Google.")
