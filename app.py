import streamlit as st
import google.generativeai as genai
from google.generativeai import client
from pypdf import PdfReader
import os

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="Asistente HNRG", page_icon="🏥")
st.title("🏥 Asistente de Enfermería")

# 1. Bypass del Error 404
if "GOOGLE_API_KEY" in st.secrets:
    genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])
    # ESTO ES LO NUEVO: Obligamos a usar la versión estable 'v1' y no la 'v1beta'
    c = client.get_default_generative_client()
    c._client_options.api_version = 'v1'
else:
    st.error("Falta la clave API en Secrets.")

def extraer_texto():
    texto_total = ""
    archivos = ["Guía de Administración de drogas HNRG 2023 (5) (1).pdf", "292+-+300+Seguridad+del+paciente.pdf"]
    for arc in archivos:
        if os.path.exists(arc):
            try:
                reader = PdfReader(arc)
                for page in reader.pages:
                    texto_total += (page.extract_text() or "") + "\n"
            except Exception: pass
    return texto_total

consulta = st.text_input("¿En qué te puedo ayudar hoy?")

if st.button("Consultar"):
    if consulta:
        with st.spinner("Buscando información..."):
            try:
                contexto = extraer_texto()
                if not contexto:
                    st.error("No se leyeron los PDFs. Revisá que estén en GitHub.")
                else:
                    # Usamos el modelo estable
                    model = genai.GenerativeModel('gemini-1.5-flash')
                    response = model.generate_content(f"Protocolos: {contexto}\nPregunta: {consulta}")
                    st.success("Respuesta:")
                    st.write(response.text)
            except Exception as e:
                st.error(f"Error persistente: {e}")
