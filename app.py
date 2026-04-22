import streamlit as st
import requests
from pypdf import PdfReader
import os

st.set_page_config(page_title="Asistente de Enfermería", page_icon="🏥", layout="wide")

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
    }
    h1 { color: #1e4f8a; }
    </style>
    """, unsafe_allow_html=True)

st.title("Asistente de Enfermería")
st.write("Consulta técnica basada en Guías de Práctica y Protocolos de Seguridad.")

api_key = st.secrets.get("GOOGLE_API_KEY")

def extraer_datos_hospital():
    texto_total = ""
    archivos_en_carpeta = os.listdir('.')
    # Expandimos las claves para que encuentre el Manual de Técnicas y Procedimientos
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
    # Aumentamos un poquito el límite de texto para que entre la info del manual nuevo
    return texto_total[:55000], encontrados

if not api_key:
    st.error("Configuración pendiente: Falta la API Key.")
else:
    with st.sidebar:
        st.header("Panel de Control")
        txt, lista = extraer_datos_hospital()
        if lista:
            st.success(f"Fuentes bibliográficas: {len(lista)}")
            for doc in lista:
                st.caption(f"✅ {doc}")
        else:
            st.error("No se detectaron archivos PDF.")

    consulta = st.text_input("Ingresá tu consulta técnica:", placeholder="Ej: Pasos para un procedimiento, dilución de drogas...")

    if st.button("Consultar"):
        if not consulta:
            st.warning("Por favor, ingresá una pregunta.")
        else:
            with st.spinner("Buscando en los manuales y protocolos..."):
                try:
                    res_models = requests.get(f"https://generativelanguage.googleapis.com/v1beta/models?key={api_key}").json()
                    modelo_activo = next((m['name'] for m in res_models.get('models', []) if 'gemini' in m['name'] and 'generateContent' in m['supportedGenerationMethods']), None)
                    
                    if modelo_activo and txt:
                        url = f"https://generativelanguage.googleapis.com/v1beta/{modelo_activo}:generateContent?key={api_key}"
                        
                        instrucciones = (
                            f"Actuá como un Asistente Técnico de Enfermería experto. "
                            f"Tu tono debe ser profesional, preciso y directo. "
                            f"USÁ ESTA BIBLIOGRAFÍA EXCLUSIVAMENTE: {txt}. "
                            f"Detallá pasos, materiales y cuidados de forma esquemática. "
                            f"Si la información no está en el texto, informá: 'Esa información no se encuentra en las guías cargadas'. "
                            f"Consulta: {consulta}"
                        )
                        
                        payload = {"contents": [{"parts": [{"text": instrucciones}]}]}
                        response = requests.post(url, json=payload)
                        data = response.json()
                        
                        if response.status_code == 200:
                            st.markdown("### 📋 Información técnica:")
                            st.markdown(f'<div class="chat-bubble">{data["candidates"][0]["content"]["parts"][0]["text"]}</div>', unsafe_allow_html=True)
                        else:
                            st.error("Error en la comunicación con la IA.")
                    elif not txt:
                        st.error("Error: No se pudo leer la bibliografía.")
                except Exception as e:
                    st.error(f"Error técnico: {e}")

st.markdown("---")
st.caption("Herramienta de soporte para la gestión del cuidado y seguridad del paciente.")
