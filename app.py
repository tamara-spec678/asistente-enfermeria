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
                # Lee todo el contenido
                for page in reader.pages:
                    content = page.extract_text()
                    if content:
                        texto_total += content + " "
                encontrados.append(archivo)
            except:
                pass
    # Bajamos apenas el límite para asegurar que la respuesta "entre" sin errores
    return texto_total[:40000], encontrados

if not api_key:
    st.error("Falta la API Key en los Secrets de Streamlit.")
else:
    with st.sidebar:
        st.header("Bibliografía Activa")
        txt, lista = extraer_datos_hospital()
        if lista:
            st.success(f"Archivos listos: {len(lista)}")
            for doc in lista:
                st.caption(f"✅ {doc}")

    consulta = st.text_input("Hacé tu consulta técnica o de dosis:")

    if st.button("Consultar"):
        if consulta:
            with st.spinner("Analizando manuales..."):
                try:
                    # Usamos la URL base más estable de Google
                    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent?key={api_key}"
                    
                    # Simplificamos el mensaje para que no haya errores de formato
                    payload = {
                        "contents": [{
                            "parts": [{
                                "text": f"Sos un enfermero experto. Usá este texto: {txt}. Consulta: {consulta}. Si es una dosis, comparala y decí si es correcta según el texto."
                            }]
                        }]
                    }
                    
                    response = requests.post(url, json=payload)
                    data = response.json()
                    
                    # Verificamos si la respuesta tiene el formato correcto
                    if "candidates" in data:
                        respuesta_final = data["candidates"][0]["content"]["parts"][0]["text"]
                        st.markdown("### 📋 Verificación:")
                        st.markdown(f'<div class="chat-bubble">{respuesta_final}</div>', unsafe_allow_html=True)
                    else:
                        st.error("La IA no pudo procesar esta consulta específica. Probá con otra pregunta.")
                except Exception as e:
                    st.error(f"Error técnico: Revisa la conexión o la API Key.")

st.markdown("---")
st.caption("Soporte para la gestión del cuidado - Hospital de Niños Ricardo Gutiérrez")
