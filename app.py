import streamlit as st
import requests
from pypdf import PdfReader
import os

st.set_page_config(page_title="Asistente de Enfermería", page_icon="🏥", layout="wide")

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

# Esta función ahora lee TODO el contenido pero lo guarda en memoria para que no tarde siempre
@st.cache_data(ttl=3600)
def extraer_datos_hospital():
    texto_total = ""
    archivos_en_carpeta = os.listdir('.')
    nombres_clave = ["Seguridad", "Guía", "292", "2023", "enfermeria", "drogas", "procedimientos", "tecnicas"]
    encontrados = []

    for archivo in archivos_en_carpeta:
        if archivo.lower().endswith('.pdf') and any(clave.lower() in archivo.lower() for clave in nombres_clave):
            try:
                reader = PdfReader(archivo)
                # LEER TODAS LAS PÁGINAS DEL PDF
                for page in reader.pages:
                    content = page.extract_text()
                    if content:
                        texto_total += content + " "
                encontrados.append(archivo)
            except:
                pass
    # Dejamos un límite generoso de 50.000 caracteres para que entre mucha info
    return texto_total[:50000], encontrados

if not api_key:
    st.error("Falta la API Key.")
else:
    with st.sidebar:
        st.header("Bibliografía Activa")
        txt, lista = extraer_datos_hospital()
        if lista:
            st.success(f"Archivos leídos: {len(lista)}")
            for doc in lista:
                st.caption(f"✅ {doc}")

    consulta = st.text_input("Consulta técnica o dosis (Ej: Aspirina 10mg en 2 años):")

    if st.button("Consultar"):
        if consulta:
            with st.spinner("Buscando en todos los manuales..."):
                try:
                    # Usamos Gemini 1.5 Flash que es el más rápido procesando mucho texto
                    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={api_key}"
                    
                    instrucciones = (
                        f"Sos un experto en enfermería pediátrica. Tu fuente es este texto: {txt}. "
                        f"Si preguntan por una dosis, buscala en el texto y comparala con la consulta. "
                        f"Responde de forma profesional, clara y directa. "
                        f"Si no encontrás el dato exacto, decilo. Consulta: {consulta}"
                    )
                    
                    payload = {"contents": [{"parts": [{"text": instrucciones}]}]}
                    response = requests.post(url, json=payload)
                    data = response.json()
                    
                    if response.status_code == 200:
                        st.markdown("### 📋 Resultado de la verificación:")
                        st.markdown(f'<div class="chat-bubble">{data["candidates"][0]["content"]["parts"][0]["text"]}</div>', unsafe_allow_html=True)
                except:
                    st.error("Hubo un problema al procesar la consulta.")
