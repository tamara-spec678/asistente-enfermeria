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
                reader = PdfReader(arc)
                for page in reader.pages:
                    texto += (page.extract_text() or "") + "\n"
            except: pass
    return texto

consulta = st.text_input("¿En qué puedo ayudarte?")

if st.button("Consultar"):
    if not api_key:
        st.error("Falta la clave API.")
    elif consulta:
        with st.spinner("Buscando en protocolos..."):
            contexto = extraer_texto()
            # PROBAMOS VARIOS MODELOS POR SI UNO FALLA
            modelos_a_probar = [
                "gemini-1.5-flash",
                "gemini-pro",
                "gemini-1.0-pro"
            ]
            
            exito = False
            for mod in modelos_a_probar:
                if exito: break
                url = f"https://generativelanguage.googleapis.com/v1beta/models/{mod}:generateContent?key={api_key}"
                payload = {"contents": [{"parts": [{"text": f"Contexto: {contexto}\n\nPregunta: {consulta}"}]}]}
                
                try:
                    res = requests.post(url, json=payload)
                    if res.status_code == 200:
                        data = res.json()
                        st.success(f"✅ Respuesta (usando modelo: {mod})")
                        st.write(data['candidates'][0]['content']['parts'][0]['text'])
                        exito = True
                    else:
                        continue # Si da error 404, prueba el siguiente modelo
                except:
                    continue
            
            if not exito:
                st.error("Google no reconoce ningún modelo con tu clave. Por favor, generá una nueva clave en AI Studio.")
