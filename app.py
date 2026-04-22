import streamlit as st
import requests
from pypdf import PdfReader
import os

# Configuración de la página
st.set_page_config(page_title="Asistente HNRG - Tamara", page_icon="🏥", layout="wide")

# Estilo visual tipo "Chat de Guardia"
st.markdown("""
    <style>
    .main { background-color: #f8f9fa; }
    .stButton>button { 
        background-color: #28a745; 
        color: white; 
        font-weight: bold; 
        border-radius: 20px;
        border: none;
        height: 3em;
    }
    .stButton>button:hover { background-color: #218838; color: white; }
    .chat-bubble { 
        padding: 20px; 
        border-radius: 15px; 
        background-color: #ffffff; 
        border-left: 6px solid #28a745;
        box-shadow: 2px 2px 10px rgba(0,0,0,0.1);
        color: #333;
        font-size: 1.1em;
    }
    .header-text { color: #1e4f8a; font-weight: bold; }
    </style>
    """, unsafe_allow_html=True)

st.markdown("<h1 class='header-text'>🏥 ¡Hola Tamara! ¿Qué onda el turno?</h1>", unsafe_allow_html=True)
st.write("Decime qué necesitas pasar o qué duda tenés y me fijo qué dicen los protocolos del Gutiérrez.")

# Recuperamos la clave desde los Secrets de Streamlit
api_key = st.secrets.get("GOOGLE_API_KEY")

def extraer_texto():
    """Función para leer los PDFs y extraer el contenido técnico"""
    texto = ""
    # Asegurate de que estos nombres de archivo sean EXACTOS a los que tenés en GitHub
    archivos = ["Guía de Administración de drogas HNRG 2023 (5) (1).pdf", "292+-+300+Seguridad+del+paciente.pdf"]
    for arc in archivos:
        if os.path.exists(arc):
            try:
                pdf = PdfReader(arc)
                for page in pdf.pages:
                    content = page.extract_text()
                    if content:
                        texto += content + " "
            except Exception:
                pass
    return texto[:40000] # Limitamos para no saturar la API

if not api_key:
    st.error("⚠️ Che Tami, no encontré la clave API en los Secrets. Revisalo en la configuración de Streamlit.")
else:
    # Espacio para la consulta
    consulta = st.text_input("Consultame lo que quieras:", placeholder="Ej: 'Che, ¿cómo paso la dipirona?' o 'Pasame los pasos para identificar al paciente'")

    if st.button("Sacame la duda 🚀"):
        if not consulta:
            st.warning("Escribí algo en el cuadro de arriba, ¡no soy adivino! 😂")
        else:
            with st.spinner("Bancame que busco en la guía..."):
                try:
                    # 1. Buscamos el modelo activo (como el sistema detectó que tenés 38, esto elige el mejor)
                    res_models = requests.get(f"https://generativelanguage.googleapis.com/v1beta/models?key={api_key}").json()
                    modelo_activo = next((m['name'] for m in res_models.get('models', []) if 'gemini' in m['name'] and 'generateContent' in m['supportedGenerationMethods']), None)
                    
                    if modelo_activo:
                        contexto = extraer_texto()
                        url = f"https://generativelanguage.googleapis.com/v1beta/{modelo_activo}:generateContent?key={api_key}"
                        
                        # EL PROMPT: Aquí es donde definimos que te hable coloquial
                        instrucciones = (
                            f"Actuá como un enfermero con mucha experiencia del Hospital de Niños Ricardo Gutiérrez que le está dando una mano a su colega Tamara. "
                            f"Tu tono debe ser súper coloquial, cercano, de confianza y directo, como si estuvieran charlando en el office de enfermería. "
                            f"USÁ EXCLUSIVAMENTE esta bibliografía oficial del hospital: {contexto}. "
                            f"Si Tamara te pregunta por una medicación, decile la dilución, tiempo de administración y cuidados, de forma clara y punteada. "
                            f"Si la información no está en los papeles, decile: 'Che Tami, me mataste, eso no lo encontré en la guía'. "
                            f"Pregunta de Tamara: {consulta}"
                        )
                        
                        payload = {
                            "contents": [{"parts": [{"text": instrucciones}]}],
                            "generationConfig": {
                                "temperature": 0.7,
                                "topP": 0.8,
                                "topK": 40
                            }
                        }
                        
                        response = requests.post(url, json=payload)
                        data = response.json()
                        
                        if response.status_code == 200:
                            respuesta_final = data["candidates"][0]["content"]["parts"][0]['text']
                            st.markdown("### 📝 Lo que encontré en la guía:")
                            st.markdown(f'<div class="chat-bubble">{respuesta_final}</div>', unsafe_allow_html=True)
                            st.caption(f"PD: Usé el modelo {modelo_activo.split('/')[-1]} para responderte.")
                        else:
                            error_msg = data.get('error', {}).get('message', 'Error desconocido')
                            st.error(f"Hubo un lío con Google: {error_msg}")
                    else:
                        st.error("No encontré ningún modelo de Gemini disponible en tu cuenta.")
                        
                except Exception as e:
                    st.error(f"Se tildó la conexión. Probá de nuevo en un ratito. Error: {e}")

# Pie de página
st.markdown("---")
st.caption("Asistente desarrollado para el Concurso Docente - HNRG 2026")
