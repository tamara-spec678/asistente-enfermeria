import streamlit as st
import requests
from pypdf import PdfReader
import os

# Configuración de página con estilo profesional
st.set_page_config(page_title="Asistente Técnico HNRG", page_icon="🏥", layout="wide")

# Estilo visual personalizado
st.markdown("""
    <style>
    .main { background-color: #f0f2f6; }
    .stButton>button { width: 100%; background-color: #007bff; color: white; border-radius: 10px; }
    .res-box { padding: 20px; border-radius: 10px; background-color: white; border-left: 5px solid #007bff; }
    </style>
    """, unsafe_allow_html=True)

st.title("🏥 Asistente Virtual de Enfermería - HNRG")
st.subheader("Consultoría técnica basada en protocolos institucionales")

api_key = st.secrets.get("GOOGLE_API_KEY")

def extraer_texto():
    texto = ""
    archivos = ["Guía de Administración de drogas HNRG 2023 (5) (1).pdf", "292+-+300+Seguridad+del+paciente.pdf"]
    for arc in archivos:
        if os.path.exists(arc):
            try:
                pdf = PdfReader(arc)
                for page in pdf.pages:
                    content = page.extract_text()
                    if content: texto += content + " "
            except: pass
    return texto[:40000] # Un poco más de margen para mayor precisión

if not api_key:
    st.error("⚠️ Error de configuración: Falta la API Key.")
else:
    # Sidebar con información útil
    with st.sidebar:
        st.header("Información del Sistema")
        st.info("Este asistente utiliza inteligencia artificial para analizar los protocolos de Seguridad del Paciente y la Guía de Drogas 2023.")
        st.warning("Recuerde: Esta es una herramienta de apoyo. Siempre prevalece el criterio clínico y la supervisión del servicio.")

    # Área de consulta
    col1, col2 = st.columns([2, 1])
    with col1:
        consulta = st.text_input("Ingresá tu duda técnica:", placeholder="Ej: Pasos para la identificación del paciente...")
    
    with col2:
        st.write(" ") # Espaciador
        boton = st.button("Consultar Bibliografía")

    if boton:
        if consulta:
            with st.spinner("Analizando protocolos oficiales..."):
                try:
                    # Sistema de auto-detección de modelo que ya sabemos que funciona
                    res_models = requests.get(f"https://generativelanguage.googleapis.com/v1beta/models?key={api_key}").json()
                    modelo_activo = next((m['name'] for m in res_models.get('models', []) if 'gemini' in m['name'] and 'generateContent' in m['supportedGenerationMethods']), None)
                    
                    if modelo_activo:
                        contexto = extraer_texto()
                        url = f"https://generativelanguage.googleapis.com/v1beta/{modelo_activo}:generateContent?key={api_key}"
                        
                        # INSTRUCCIONES AVANZADAS (System Prompt)
                        instrucciones = (
                            f"Sos un Asistente Técnico de Enfermería del Hospital de Niños Ricardo Gutiérrez. "
                            f"Tu objetivo es responder de forma precisa, breve y profesional. "
                            f"USÁ EXCLUSIVAMENTE este contexto bibliográfico: {contexto}. "
                            f"Si la información no está en el texto, respondé: 'Lo siento, esa información no se encuentra en los protocolos cargados'. "
                            f"Duda del enfermero: {consulta}"
                        )
                        
                        payload = {"contents": [{"parts": [{"text": instrucciones}]}]}
                        response = requests.post(url, json=payload)
                        data = response.json()
                        
                        if response.status_code == 200:
                            st.markdown("### 📋 Respuesta Técnica:")
                            st.markdown(f'<div class="res-box">{data["candidates"][0]["content"]["parts"][0]["text"]}</div>', unsafe_allow_html=True)
                            st.caption(f"Fuente consultada: {modelo_activo.split('/')[-1]}")
                        else:
                            st.error("Error en la respuesta del servidor.")
                except Exception as e:
                    st.error(f"Error de conexión: {e}")
