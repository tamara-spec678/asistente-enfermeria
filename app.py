import streamlit as st
import requests
from pypdf import PdfReader
import os

st.set_page_config(page_title="Asistente de Enfermería", page_icon="🏥", layout="wide")

# Estilo visual
st.markdown("""
    <style>
    .stButton>button { background-color: #1e4f8a; color: white; font-weight: bold; border-radius: 10px; width: 100%; height: 3em; }
    .chat-bubble { padding: 20px; border-radius: 12px; background-color: #ffffff; border-left: 6px solid #1e4f8a; box-shadow: 2px 2px 8px rgba(0,0,0,0.05); color: #333; }
    </style>
    """, unsafe_allow_html=True)

st.title("Asistente de Enfermería 🏥")

api_key = st.secrets.get("GOOGLE_API_KEY")

@st.cache_data(ttl=3600)
def extraer_todo_el_manual():
    texto_total = ""
    archivos = [f for f in os.listdir('.') if f.lower().endswith('.pdf')]
    encontrados = []
    for archivo in archivos:
        try:
            reader = PdfReader(archivo)
            for page in reader.pages:
                content = page.extract_text()
                if content: texto_total += content + " "
            encontrados.append(archivo)
        except: pass
    # Límite de 40k: Es mucho texto pero no tanto como para que la clave gratuita explote
    return texto_total[:40000], encontrados

if not api_key:
    st.error("Falta la API Key.")
else:
    with st.sidebar:
        st.header("Bibliografía")
        txt, lista = extraer_todo_el_manual()
        for d in lista: st.caption(f"✅ {d}")

    consulta = st.text_input("Ingresá tu consulta técnica:")

    if st.button("Consultar"):
        if consulta and txt:
            with st.spinner("Buscando en manuales..."):
                try:
                    # Usamos el modelo 1.5-flash: es RÁPIDO y aguanta más preguntas seguidas
                    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={api_key}"
                    
                    prompt = (
                        f"Sos un Asistente Técnico de Enfermería. Basate solo en este texto: {txt}. "
                        f"Consulta: {consulta}. Si es una dosis, comparala y da la respuesta exacta del manual. "
                        f"Si no está, decilo profesionalmente."
                    )
                    
                    payload = {"contents": [{"parts": [{"text": prompt}]}]}
                    response = requests.post(url, json=payload)
                    data = response.json()
                    
                    if "candidates" in data:
                        respuesta = data["candidates"][0]["content"]["parts"][0]["text"]
                        st.markdown(f'<div class="chat-bubble">{respuesta}</div>', unsafe_allow_html=True)
                    else:
                        st.warning("Google pide un respiro (60 segundos). Esperá un ratito y volvé a intentar.")
                except:
                    st.error("Error de conexión.")
