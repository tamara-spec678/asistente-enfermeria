import streamlit as st
import requests
from pypdf import PdfReader
import os

st.set_page_config(page_title="Asistente de Enfermería", page_icon="🏥")

st.title("Asistente de Enfermería 🏥")

api_key = st.secrets.get("GOOGLE_API_KEY")

@st.cache_data(ttl=3600)
def extraer_datos_optimizados(busqueda=""):
    texto_relevante = ""
    archivos = [f for f in os.listdir('.') if f.lower().endswith('.pdf')]
    encontrados = []

    for archivo in archivos:
        try:
            reader = PdfReader(archivo)
            for page in reader.pages:
                content = page.extract_text()
                if content:
                    # SI NO HAY BUSQUEDA, TOMAMOS UN POCO DE CADA PAGINA
                    # SI HAY BUSQUEDA, SOLO TOMAMOS DONDE APARECE LA PALABRA
                    if not busqueda or busqueda.lower() in content.lower():
                        texto_relevante += content + " "
            encontrados.append(archivo)
        except: pass
    
    # LIMITAMOS A 15.000 CARACTERES (Súper liviano para que la clave gratuita vuele)
    return texto_relevante[:15000], encontrados

if not api_key:
    st.error("Configurá la API Key.")
else:
    consulta = st.text_input("Ingresá fármaco o técnica (ej: Dipirona):")

    if st.button("Consultar"):
        if consulta:
            with st.spinner("Buscando de forma ultra-rápida..."):
                # Primero extraemos solo lo que sirve para esa consulta
                txt_recortado, lista = extraer_datos_optimizados(consulta.split()[0]) # Busca la primera palabra
                
                try:
                    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent?key={api_key}"
                    
                    payload = {
                        "contents": [{
                            "parts": [{
                                "text": f"Basado en este fragmento del manual: {txt_recortado}. Respondé de forma muy breve a: {consulta}"
                            }]
                        }]
                    }
                    
                    response = requests.post(url, json=payload)
                    data = response.json()
                    
                    if "candidates" in data:
                        res = data["candidates"][0]["content"]["parts"][0]["text"]
                        st.info(res)
                    else:
                        st.error("Google sigue pidiendo un respiro. Esperá 30 segundos y probá de nuevo.")
                except:
                    st.error("Error de conexión.")

st.sidebar.caption("Modo de bajo consumo de datos activo.")
