import streamlit as st
import requests
from pypdf import PdfReader
import os

# Configuración de la página
st.set_page_config(page_title="Asistente HNRG - Tamara", page_icon="🏥", layout="wide")

# Estilo visual "Chat de Guardia"
st.markdown("""
    <style>
    .main { background-color: #f8f9fa; }
    .stButton>button { 
        background-color: #28a745; 
        color: white; 
        font-weight: bold; 
        border-radius: 20px;
        width: 100%;
        height: 3em;
    }
    .chat-bubble { 
        padding: 20px; 
        border-radius: 15px; 
        background-color: #ffffff; 
        border-left: 6px solid #28a745;
        box-shadow: 2px 2px 10px rgba(0,0,0,0.1);
        color: #333;
    }
    </style>
    """, unsafe_allow_html=True)

st.markdown("<h1 style='color: #1e4f8a;'>🏥 ¡Hola Tamara!</h1>", unsafe_allow_html=True)

api_key = st.secrets.get("GOOGLE_API_KEY")

def extraer_datos_hospital():
    """Busca los PDFs sin importar si el nombre tiene signos raros"""
    texto_total = ""
    archivos_en_carpeta = os.listdir('.') # Listamos todo lo que hay en el GitHub
    
    # Estos son los fragmentos clave de tus nombres de archivo
    nombres_clave = ["Seguridad", "Guía", "292", "2023"]
    encontrados = []

    for archivo in archivos_en_carpeta:
        # Si el archivo es PDF y coincide con alguna de nuestras palabras clave
        if archivo.lower().endswith('.pdf') and any(clave.lower() in archivo.lower() for clave in nombres_clave):
            try:
                reader = PdfReader(archivo)
                for page in reader.pages:
                    content = page.extract_text()
                    if content:
                        texto_total += content + " "
                encontrados.append(archivo)
            except:
                pass
    
    return texto_total[:45000], encontrados

if not api_key:
    st.error("⚠️ No hay API Key cargada en los Secrets.")
else:
    # Sidebar de diagnóstico (Solo para que vos veas si cargó los archivos)
    with st.sidebar:
        st.header("🩺 Triage del Sistema")
        txt, lista = extraer_datos_hospital()
        if lista:
            st.success(f"Archivos leídos: {len(lista)}")
            for l in lista: st.write(f"✅ {l}")
        else:
            st.error("❌ No encontré los PDFs en GitHub.")
            st.write("Archivos vistos:", os.listdir('.'))

    consulta = st.text_input("¿Qué duda tenés del turno?", placeholder="Ej: ¿Cómo paso la dipirona?")

    if st.button("Sacame la duda 🚀"):
        if not consulta:
            st.warning("Escribí algo primero, Tami.")
        else:
            with st.spinner("Bancame que busco en los papeles..."):
                try:
                    # Detectamos el modelo activo
                    res_models = requests.get(f"https://generativelanguage.googleapis.com/v1beta/models?key={api_key}").json()
                    modelo_activo = next((m['name'] for m in res_models.get('models', []) if 'gemini' in m['name'] and 'generateContent' in m['supportedGenerationMethods']), None)
                    
                    if modelo_activo and txt:
                        url = f"https://generativelanguage.googleapis.com/v1beta/{modelo_activo}:generateContent?key={api_key}"
                        
                        instrucciones = (
                            f"Actuá como un enfermero experto del HNRG. Hablale a tu colega Tamara de forma coloquial y cercana. "
                            f"USÁ ESTA BIBLIOGRAFÍA: {txt}. "
                            f"Si te preguntan por una droga o protocolo, buscá los pasos exactos (dilución, tiempo, cuidados). "
                            f"Si no está, decí: 'Che Tami, no lo encuentro en la guía, fijate si está bien escrito'."
                            f"Duda: {consulta}"
                        )
                        
                        payload = {"contents": [{"parts": [{"text": instrucciones}]}]}
                        response = requests.post(url, json=payload)
                        data = response.json()
                        
                        if response.status_code == 200:
                            st.markdown("### 📝 Lo que dice el protocolo:")
                            st.markdown(f'<div class="chat-bubble">{data["candidates"][0]["content"]["parts"][0]["text"]}</div>', unsafe_allow_html=True)
                        else:
                            st.error("Google se tildó. Probá de nuevo.")
                    elif not txt:
                        st.error("No puedo responder porque no logré leer los PDFs en GitHub.")
                except Exception as e:
                    st.error(f"Error: {e}")

st.markdown("---")
st.caption("Prototipo para Concurso Docente HNRG")
