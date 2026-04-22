import streamlit as st
import requests
from pypdf import PdfReader
import os

# Configuración de la página
st.set_page_config(page_title="Asistente de Enfermería", page_icon="🏥", layout="wide")

# Estilo visual profesional
st.markdown("""
    <style>
    .main { background-color: #f8f9fa; }
    .stButton>button { 
        background-color: #1e4f8a; 
        color: white; 
        font-weight: bold; 
        border-radius: 10px;
        width: 100%;
        height: 3em;
    }
    .chat-bubble { 
        padding: 20px; 
        border-radius: 12px; 
        background-color: #ffffff; 
        border-left: 6px solid #1e4f8a;
        box-shadow: 2px 2px 8px rgba(0,0,0,0.05);
        color: #333;
        line-height: 1.6;
    }
    h1 { color: #1e4f8a; }
    </style>
    """, unsafe_allow_html=True)

# TÍTULO CON EMOJI
st.title("Asistente de Enfermería 🏥")
st.write("Consulta técnica basada en Guías de Práctica y Protocolos de Seguridad.")

api_key = st.secrets.get("GOOGLE_API_KEY")

def extraer_datos_hospital():
    """Busca y lee los PDFs cargados en GitHub"""
    texto_total = ""
    archivos_en_carpeta = os.listdir('.')
    # Palabras clave para identificar tus manuales y protocolos
    nombres_clave = ["Seguridad", "Guía", "292", "2023", "enfermeria", "drogas", "procedimientos", "tecnicas"]
    encontrados = []

    for archivo in archivos_en_carpeta:
        if archivo.lower().endswith('.pdf') and any(clave.lower() in archivo.lower() for clave in nombres_clave):
            try:
                reader = PdfReader(archivo)
                for page in reader.pages:
                    content = page.extract_text()
                    if content:
                        texto_total += content + " "
                encontrados.append(archivo)
            except:
                pass
    # Limitamos el texto para que la respuesta sea más rápida
    return texto_total[:45000], encontrados

if not api_key:
    st.error("Configuración pendiente: Falta la API Key en los Secrets.")
else:
    # Panel lateral para control de bibliografía
    with st.sidebar:
        st.header("Bibliografía Activa")
        txt, lista = extraer_datos_hospital()
        if lista:
            st.success(f"Fuentes detectadas: {len(lista)}")
            for doc in lista:
                st.caption(f"✅ {doc}")
        else:
            st.error("No se detectaron archivos PDF.")

    # Campo de consulta
    consulta = st.text_input("Ingresá tu consulta técnica:", placeholder="Ej: Pasos para colocar una sonda, dilución de fármacos...")

    if st.button("Consultar"):
        if not consulta:
            st.warning("Por favor, ingresá una pregunta.")
        else:
            with st.spinner("Consultando manuales..."):
                try:
                    # Detectar modelo disponible
                    res_models = requests.get(f"https://generativelanguage.googleapis.com/v1beta/models?key={api_key}").json()
                    modelo_activo = next((m['name'] for m in res_models.get('models', []) if 'gemini' in m['name'] and 'generateContent' in m['supportedGenerationMethods']), None)
                    
                    if modelo_activo and txt:
                        url = f"https://generativelanguage.googleapis.com/v1beta/{modelo_activo}:generateContent?key={api_key}"
                        
                        # Instrucciones de comportamiento
                        instrucciones = (
                            f"Actuá como un Asistente Técnico de Enfermería experto. "
                            f"Tu tono debe ser profesional, preciso y directo. "
                            f"USÁ ESTA BIBLIOGRAFÍA EXCLUSIVAMENTE: {txt}. "
                            f"Si se consulta sobre un fármaco o técnica, detallá pasos, materiales y cuidados de forma esquemática. "
                            f"Si la información no está en el texto, informá que no se encuentra en las guías cargadas. "
                            f"Consulta: {consulta}"
                        )
                        
                        payload = {"contents": [{"parts": [{"text": instrucciones}]}]}
                        response = requests.post(url, json=payload)
                        data = response.json()
                        
                        if response.status_code == 200:
                            st.markdown("### 📋 Información técnica:")
                            st.markdown(f'<div class="chat-bubble">{data["candidates"][0]["content"]["parts"][0]["text"]}</div>', unsafe_allow_html=True)
                        else:
                            st.error("Error de comunicación con la IA.")
                    elif not txt:
                        st.error("No se pudo procesar la bibliografía.")
                except Exception as e:
                    st.error(f"Error técnico: {e}")

st.markdown("---")
st.caption("Herramienta de soporte para la gestión del cuidado y seguridad del paciente.")
