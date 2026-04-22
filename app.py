import streamlit as st
import requests
from pypdf import PdfReader
import os

st.set_page_config(page_title="Asistente HNRG", page_icon="🏥")
st.title("🏥 Asistente de Enfermería")

api_key = st.secrets.get("GOOGLE_API_KEY")

def extraer_texto():
    texto = ""
    archivos = ["Guía de Administración de drogas HNRG 2023 (5) (1).pdf", "292+-+300+Seguridad+del+paciente.pdf"]
    for arc in archivos:
        if os.path.exists(arc):
            try:
                pdf = PdfReader(arc)
                for page in pdf.pages:
                    texto += (page.extract_text() or "") + " "
            except: pass
    return texto[:30000]

if not api_key:
    st.error("⚠️ Configura la clave API en Secrets.")
else:
    # 1. Función para encontrar qué modelo tenés activo de esos 38
    def obtener_modelo_valido():
        try:
            url = f"https://generativelanguage.googleapis.com/v1beta/models?key={api_key}"
            res = requests.get(url).json()
            for m in res.get('models', []):
                # Buscamos uno que sea 'gemini' y que permita generar contenido
                if 'gemini' in m['name'] and 'generateContent' in m['supportedGenerationMethods']:
                    return m['name'] # Retorna algo como 'models/gemini-1.5-flash-latest'
            return None
        except:
            return None

    consulta = st.text_input("¿Qué consulta técnica tenés?")

    if st.button("Consultar Protocolos"):
        if consulta:
            with st.spinner("Conectando con Google AI..."):
                modelo_activo = obtener_modelo_valido()
                
                if not modelo_activo:
                    st.error("No se encontró un modelo compatible en tu cuenta.")
                else:
                    try:
                        contexto = extraer_texto()
                        # Usamos el nombre exacto que Google nos dio
                        url = f"https://generativelanguage.googleapis.com/v1beta/{modelo_activo}:generateContent?key={api_key}"
                        
                        payload = {
                            "contents": [{"parts": [{"text": f"Contexto HNRG: {contexto}\n\nPregunta: {consulta}"}]}]
                        }
                        
                        response = requests.post(url, json=payload)
                        data = response.json()
                        
                        if response.status_code == 200:
                            st.success(f"✅ Respuesta (vía {modelo_activo.split('/')[-1]}):")
                            st.write(data['candidates'][0]['content']['parts'][0]['text'])
                        else:
                            st.error(f"Google dice: {data['error']['message']}")
                    except Exception as e:
                        st.error(f"Error: {e}")
