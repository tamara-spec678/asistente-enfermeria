import streamlit as st
import google.generativeai as genai
from pypdf import PdfReader
import os

# Configuración básica
st.set_page_config(page_title="Asistente HNRG", page_icon="🏥")
st.title("🏥 Asistente de Enfermería")

# 1. Configurar la Clave
if "GOOGLE_API_KEY" in st.secrets:
    genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])
else:
    st.error("Falta la clave API en Secrets.")

# 2. Función para leer PDFs
def extraer_texto():
    texto_total = ""
    # Asegurate que estos nombres sean EXACTOS a los de tus archivos en GitHub
    archivos = ["Guía de Administración de drogas HNRG 2023 (5) (1).pdf", "292+-+300+Seguridad+del+paciente.pdf"]
    for arc in archivos:
        if os.path.exists(arc):
            try:
                pdf = PdfReader(arc)
                for pagina in pdf.pages:
                    texto_total += (pagina.extract_text() or "") + "\n"
            except Exception:
                pass
    return texto_total

# 3. Interfaz
consulta = st.text_input("Escribí tu duda técnica (ej: Dilución de dopamina):")

if st.button("Consultar Protocolos"):
    if consulta:
        with st.spinner("Buscando en los archivos del hospital..."):
            try:
                contexto = extraer_texto()
                if not contexto:
                    st.error("No se pudo leer el contenido de los PDFs. Revisá los nombres en GitHub.")
                else:
                    # Usamos el modelo estable
                    model = genai.GenerativeModel('gemini-1.5-flash')
                    prompt = f"Actuá como un enfermero tutor del HNRG. Basándote en esto: {contexto}\n\nPregunta: {consulta}"
                    response = model.generate_content(prompt)
                    st.success("Resultado:")
                    st.write(response.text)
            except Exception as e:
                st.error(f"Error: {e}")
