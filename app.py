import streamlit as st
import requests
from pypdf import PdfReader
import os
import time

st.set_page_config(page_title="Asistente de Enfermería", page_icon="🏥")

st.title("Asistente de Enfermería 🏥")
st.caption("Versión Optimizada - Soporte Hospital Gutiérrez")

api_key = st.secrets.get("GOOGLE_API_KEY")

# Esta función busca la palabra clave para no saturar a Google con texto innecesario
@st.cache_data(ttl=3600)
def buscar_texto_relevante(consulta):
    texto_breve = ""
    palabra_clave = consulta.split()[0].lower() # Toma la primera palabra (ej: Dipirona)
    archivos = [f for f in os.listdir('.') if f.lower().endswith('.pdf')]
    
    for archivo in archivos:
        try:
            reader = PdfReader(archivo)
            for page in reader.pages:
                texto_pag = page.extract_text()
                if texto_pag and palabra_clave in texto_pag.lower():
                    texto_breve += texto_pag + " "
                    if len(texto_breve) > 8000: break # Cortamos rápido para que sea liviano
        except: pass
    return texto_breve[:10000]

if not api_key:
    st.error("Falta la configuración de la clave.")
else:
    consulta = st.text_input("Ingresá tu duda (ej: Dosis Dipirona):")

    if st.button("Consultar"):
        if consulta:
            with st.spinner("Buscando en manuales..."):
                # 1. Buscamos solo lo importante del PDF
                contexto_mini = buscar_texto_relevante(consulta)
                
                # 2. Intentamos la consulta con el modelo más rápido
                try:
                    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={api_key}"
                    
                    prompt = f"Contexto: {contexto_mini}\n\nPregunta: {consulta}\n\nRespuesta técnica muy breve:"
                    
                    payload = {"contents": [{"parts": [{"text": prompt}]}]}
                    response = requests.post(url, json=payload)
                    data = response.json()
                    
                    if "candidates" in data:
                        resultado = data["candidates"][0]["content"]["parts"][0]["text"]
                        st.success(resultado)
                    elif "error" in data and data["error"]["code"] == 429:
                        st.warning("⚠️ Google está saturado. Esperá 15 segundos y volvé a tocar el botón.")
                    else:
                        st.error("No se pudo obtener respuesta. Intentá simplificar la pregunta.")
                except:
                    st.error("Error de conexión.")

st.sidebar.warning("Nota: La versión gratuita permite 2 o 3 consultas por minuto. Si da error, solo hay que esperar unos segundos.")
