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
                    texto += (page.extract_text() or "") + "\n"
            except: pass
    return texto

if not api_key:
    st.error("⚠️ No se encontró la clave API en los Secrets de Streamlit.")
else:
    # 1. PASO MÉDICO: Ver qué modelos están "vivos" para tu clave
    with st.expander("🩺 Estado de la conexión con Google"):
        try:
            list_url = f"https://generativelanguage.googleapis.com/v1beta/models?key={api_key}"
            res_list = requests.get(list_url)
            modelos_data = res_list.json()
            
            if res_list.status_code == 200:
                # Sacamos la lista de nombres de modelos disponibles
                modelos_disponibles = [m['name'] for m in modelos_data.get('models', []) if 'generateContent' in m.get('supportedGenerationMethods', [])]
                st.success(f"Conexión activa. Modelos encontrados: {len(modelos_disponibles)}")
                # Elegimos el mejor disponible automáticamente
                modelo_a_usar = modelos_disponibles[0] if modelos_disponibles else None
            else:
                st.error(f"Error de validación: {modelos_data.get('error', {}).get('message')}")
                modelo_a_usar = None
        except:
            st.error("No se pudo contactar al servidor de Google.")
            modelo_a_usar = None

    # 2. INTERFAZ DE CONSULTA
    consulta = st.text_input("¿Qué consulta técnica tenés?")

    if st.button("Consultar Protocolos"):
        if not modelo_a_usar:
            st.error("No hay modelos disponibles. Revisá tu API Key en AI Studio.")
        elif not consulta:
            st.warning("Escribí una consulta.")
        else:
            with st.spinner("Procesando..."):
                try:
                    contexto = extraer_texto()
                    # Usamos el modelo que el sistema detectó como activo
                    url = f"https://generativelanguage.googleapis.com/{modelo_a_usar}:generateContent?key={api_key}"
                    
                    payload = {
                        "contents": [{"parts": [{"text": f"Basándote en este contexto del HNRG: {contexto}\n\nPregunta: {consulta}"}]}]
                    }
                    
                    response = requests.post(url, json=payload)
                    data = response.json()
                    
                    if response.status_code == 200:
                        st.success("✅ Respuesta obtenida")
                        st.write(data['candidates'][0]['content']['parts'][0]['text'])
                    else:
                        st.error(f"Detalle técnico: {data.get('error', {}).get('message')}")
                except Exception as e:
                    st.error(f"Error: {e}")
