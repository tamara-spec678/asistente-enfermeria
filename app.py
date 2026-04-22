import streamlit as st
import requests
from pypdf import PdfReader
import os

st.set_page_config(page_title="Asistente de Enfermería", page_icon="🏥", layout="wide")

st.markdown("""
    <style>
    .main { background-color: #f8f9fa; }
    .stButton>button { 
        background-color: #1e4f8a; color: white; font-weight: bold; border-radius: 10px; width: 100%; height: 3.5em;
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
    archivos_en_carpeta = [f for f in os.listdir('.') if f.lower().endswith('.pdf')]
    # Palabras clave para filtrar tus manuales del Gutiérrez
    claves = ["seguridad", "guía", "292", "2023", "enfermeria", "drogas", "procedimientos", "tecnicas"]
    encontrados = []

    for archivo in archivos_en_carpeta:
        if any(c in archivo.lower() for c in claves):
            try:
                reader = PdfReader(archivo)
                for page in reader.pages:
                    content = page.extract_text()
                    if content: texto_total += content + " "
                encontrados.append(archivo)
            except: pass
    # Usamos un límite alto pero seguro para el modelo Flash
    return texto_total[:100000], encontrados

if not api_key:
    st.error("Error: Configura la GOOGLE_API_KEY en Secrets.")
else:
    with st.sidebar:
        st.header("Bibliografía Cargada")
        txt_bibliografia, lista_docs = extraer_datos_hospital()
        if lista_docs:
            st.success(f"Archivos listos: {len(lista_docs)}")
            for d in lista_docs: st.caption(f"✅ {d}")
        else:
            st.warning("No se encontraron los manuales. Verifica los nombres de los archivos.")

    consulta = st.text_input("Ingresá tu duda (ej: dosis de dipirona en 10 años):")

    if st.button("Consultar"):
        if not consulta:
            st.warning("Por favor escribí una pregunta.")
        elif not txt_bibliografia:
            st.error("No hay texto para analizar. Subí los PDFs a GitHub.")
        else:
            with st.spinner("Buscando en los manuales del hospital..."):
                try:
                    # Usamos el modelo 1.5-flash que es el más potente y rápido para PDF largos
                    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={api_key}"
                    
                    prompt_final = (
                        f"Sos un experto en enfermería del Hospital Gutiérrez. "
                        f"Basándote EXCLUSIVAMENTE en este texto: {txt_bibliografia}. "
                        f"Respondé a la siguiente consulta de forma profesional y precisa: {consulta}. "
                        f"Si preguntan por dosis, buscá la tabla correspondiente en el texto y decí los valores exactos."
                    )
                    
                    payload = {"contents": [{"parts": [{"text": prompt_final}]}]}
                    response = requests.post(url, json=payload)
                    data = response.json()
                    
                    if "candidates" in data:
                        respuesta = data["candidates"][0]["content"]["parts"][0]["text"]
                        st.markdown("### 📋 Resultado de la consulta:")
                        st.markdown(f'<div class="chat-bubble">{respuesta}</div>', unsafe_allow_html=True)
                    else:
                        st.error("La IA no pudo procesar esta consulta específica. Probá simplificando la pregunta.")
                except Exception as e:
                    st.error(f"Error técnico de conexión. Reintentá en unos segundos.")

st.markdown("---")
st.caption("Herramienta de soporte - Hospital de Niños Ricardo Gutiérrez")
