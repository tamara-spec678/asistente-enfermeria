import streamlit as st
import requests
from pypdf import PdfReader
import os

st.set_page_config(page_title="Asistente de Enfermería", page_icon="🏥")

st.markdown("""
    <style>
    .stButton>button { background-color: #1e4f8a; color: white; font-weight: bold; border-radius: 10px; width: 100%; }
    .chat-bubble { padding: 20px; border-radius: 12px; background-color: #ffffff; border-left: 6px solid #1e4f8a; box-shadow: 2px 2px 8px rgba(0,0,0,0.05); color: #333; }
    </style>
    """, unsafe_allow_html=True)

st.title("Asistente de Enfermería 🏥")

api_key = st.secrets.get("GOOGLE_API_KEY")

@st.cache_data(ttl=3600)
def extraer_datos_hospital():
    texto_total = ""
    # Buscamos todos los PDFs
    archivos = [f for f in os.listdir('.') if f.lower().endswith('.pdf')]
    encontrados = []

    for archivo in archivos:
        try:
            reader = PdfReader(archivo)
            # Para no saturar la clave gratuita, leemos lo más importante de cada manual
            for i, page in enumerate(reader.pages):
                if i > 60: break # Si el manual tiene más de 60 páginas, cortamos para que no de error
                content = page.extract_text()
                if content: texto_total += content + " "
            encontrados.append(archivo)
        except: pass
    # Límite de seguridad para que la clave gratuita de Google NO rechace el pedido
    return texto_total[:35000], encontrados

if not api_key:
    st.error("Falta la configuración de la clave API.")
else:
    with st.sidebar:
        st.header("Bibliografía")
        txt_bibliografia, lista_docs = extraer_datos_hospital()
        for d in lista_docs: st.caption(f"✅ {d}")

    consulta = st.text_input("Ingresá tu duda técnica:")

    if st.button("Consultar"):
        if consulta and txt_bibliografia:
            with st.spinner("Buscando respuesta..."):
                try:
                    # Usamos el modelo estándar que acepta tu clave
                    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent?key={api_key}"
                    
                    payload = {
                        "contents": [{
                            "parts": [{
                                "text": f"Contexto técnico: {txt_bibliografia}\n\nPregunta: {consulta}\n\nResponde de forma corta y profesional usando el contexto."
                            }]
                        }]
                    }
                    
                    response = requests.post(url, json=payload)
                    data = response.json()
                    
                    if "candidates" in data:
                        res = data["candidates"][0]["content"]["parts"][0]["text"]
                        st.markdown(f'<div class="chat-bubble">{res}</div>', unsafe_allow_html=True)
                    else:
                        st.warning("La clave gratuita está saturada. Intentá con una pregunta más corta o reintentá en un minuto.")
                except:
                    st.error("Error de conexión con Google.")
