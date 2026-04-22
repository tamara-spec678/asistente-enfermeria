import streamlit as st
import requests
from pypdf import PdfReader
import os

st.set_page_config(page_title="Asistente de Enfermería", page_icon="🏥")

st.title("Asistente de Enfermería 🏥")

api_key = st.secrets.get("GOOGLE_API_KEY")

@st.cache_data(ttl=3600)
def cargar_biblioteca():
    """Lee los archivos una sola vez y los guarda en la memoria de la app"""
    biblioteca = []
    archivos = [f for f in os.listdir('.') if f.lower().endswith('.pdf')]
    for archivo in archivos:
        try:
            reader = PdfReader(archivo)
            for page in reader.pages:
                texto = page.extract_text()
                if texto:
                    biblioteca.append(texto)
        except: pass
    return biblioteca

if not api_key:
    st.error("Falta la API Key.")
else:
    # Cargamos los datos en silencio
    datos = cargar_biblioteca()
    
    consulta = st.text_input("Ingresá tu duda (ej: Dosis Dipirona):")

    if st.button("Consultar"):
        if consulta:
            with st.spinner("Buscando información específica..."):
                # BUSQUEDA INTELIGENTE: Solo mandamos a la IA las páginas que mencionan la duda
                palabra_clave = consulta.split()[0].lower()
                contexto_relevante = ""
                for pagina in datos:
                    if palabra_clave in pagina.lower():
                        contexto_relevante += pagina + " "
                        if len(contexto_relevante) > 10000: break # No nos pasamos del límite
                
                if not contexto_relevante:
                    # Si no encuentra la palabra, le mandamos un pedacito general
                    contexto_relevante = " ".join(datos)[:5000]

                try:
                    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={api_key}"
                    payload = {
                        "contents": [{
                            "parts": [{"text": f"Contexto: {contexto_relevante}\n\nPregunta: {consulta}\n\nResponde como enfermero experto de forma breve."}]
                        }]
                    }
                    response = requests.post(url, json=payload)
                    data = response.json()
                    
                    if "candidates" in data:
                        st.info(data["candidates"][0]["content"]["parts"][0]["text"])
                    else:
                        st.warning("⚠️ Google está saturado. Esperá 20 segundos y reintentá.")
                except:
                    st.error("Error de conexión.")
