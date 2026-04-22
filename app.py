import streamlit as st
import requests
from pypdf import PdfReader
import os

# Configuración de la página
st.set_page_config(page_title="Asistente de Enfermería", page_icon="🏥", layout="wide")

# Estilo visual que ya tenías
st.markdown("""
    <style>
    .main { background-color: #f8f9fa; }
    .stButton>button { 
        background-color: #1e4f8a; color: white; font-weight: bold; border-radius: 10px; width: 100%; height: 3em;
    }
    .chat-bubble { 
        padding: 20px; border-radius: 12px; background-color: #ffffff; border-left: 6px solid #1e4f8a;
        box-shadow: 2px 2px 8px rgba(0,0,0,0.05); color: #333; line-height: 1.6;
    }
    </style>
    """, unsafe_allow_html=True)

st.title("Asistente de Enfermería 🏥")

api_key = st.secrets.get("GOOGLE_API_KEY")

def extraer_datos_hospital():
    """Busca y lee los PDFs en el repositorio como al principio"""
    texto_total = ""
    archivos_en_carpeta = os.listdir('.')
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
    # Volvemos al límite estable de caracteres
    return texto_total[:45000], encontrados

if not api_key:
    st.error("Configuración pendiente: Falta la API Key en los Secrets.")
else:
    with st.sidebar:
        st.header("Bibliografía Activa")
        txt, lista = extraer_datos_hospital()
        if lista:
            st.success(f"Fuentes detectadas: {len(lista)}")
            for doc in lista:
                st.caption(f"✅ {doc}")

    consulta = st.text_input("Ingresá tu consulta técnica:")

    if st.button("Consultar"):
        if not consulta:
            st.warning("Por favor, ingresá una pregunta.")
        else:
            with st.spinner("Buscando en manuales..."):
                try:
                    # ESTA ES LA PARTE QUE BUSCA TU MODELO DISPONIBLE AUTOMÁTICAMENTE
                    res_models = requests.get(f"https://generativelanguage.googleapis.com/v1beta/models?key={api_key}").json()
                    modelo_activo = next((m['name'] for m in res_models.get('models', []) if 'gemini' in m['name'] and 'generateContent' in m['supportedGenerationMethods']), None)
                    
                    if modelo_activo and txt:
                        url = f"https://generativelanguage.googleapis.com/v1beta/{modelo_activo}:generateContent?key={api_key}"
                        
                        instrucciones = (
                            f"Sos un asistente técnico de enfermería experto. "
                            f"USÁ ESTA BIBLIOGRAFÍA: {txt}. "
                            f"Si te preguntan por una dosis, búscala en el texto y compárala. "
                            f"Responde de forma profesional y directa: {consulta}"
                        )
                        
                        payload = {"contents": [{"parts": [{"text": instrucciones}]}]}
                        response = requests.post(url, json=payload)
                        data = response.json()
                        
                        if response.status_code == 200:
                            st.markdown("### 📋 Verificación Técnica:")
                            st.markdown(f'<div class="chat-bubble">{data["candidates"][0]["content"]["parts"][0]["text"]}</div>', unsafe_allow_html=True)
                        else:
                            st.error("La clave está saturada, espera un minuto.")
                    else:
                        st.error("No se encontró un modelo disponible o no hay texto cargado.")
                except Exception as e:
                    st.error(f"Error: {e}")

st.markdown("---")
st.caption("Hospital de Niños Ricardo Gutiérrez")
