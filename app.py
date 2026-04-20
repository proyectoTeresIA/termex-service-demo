import streamlit as st
import requests
import json
import html
import re

LOGO_URL = "https://proyectoteresia.org/wp-content/uploads/2024/05/Teresia-X-sin-fondo.png"

def highlight_terms(text, terms):
    if not terms:
        return text
    
    highlighted_text = text
    for term in terms:
        pattern = re.compile(re.escape(term), re.IGNORECASE)
        highlighted_text = pattern.sub(
            f'<span style="background-color: #00B4D8; color: white; padding: 2px 6px; border-radius: 4px; font-weight: bold;">{term}</span>',
            highlighted_text
        )
    return highlighted_text

st.set_page_config(
    page_title="TeresIA - Extracción de Términos",
    page_icon=LOGO_URL,
    layout="wide"
)

st.markdown("""
<style>
    .stApp {
        background-color: #0D1B2A;
    }
    .stSidebar {
        background-color: #1B263B;
    }
    .stSidebar .stRadio > div {
        background-color: #1B263B;
    }
    .stRadio label {
        color: #E0E1DD !important;
    }
    .stTextArea textarea {
        background-color: #1B263B;
        color: #E0E1DD;
    }
    .stSelectbox div[data-baseweb="select"] > div {
        background-color: #1B263B;
        color: #E0E1DD;
    }
    .stButton > button {
        background-color: #00B4D8;
        color: white;
        border: none;
    }
    .stButton > button:hover {
        background-color: #0096C7;
        color: white;
    }
    h1, h2, h3, h4, h5, h6, p, label {
        color: #E0E1DD !important;
    }
    .stMarkdown p {
        color: #E0E1DD !important;
    }
    .logo-container {
        text-align: center;
        padding: 20px;
    }
    .logo-container img {
        max-width: 200px;
    }
    .result-box {
        background-color: #1B263B;
        padding: 20px;
        border-radius: 10px;
        border: 1px solid #00B4D8;
        margin-top: 20px;
    }
    .result-box h3 {
        color: #00B4D8 !important;
    }
    .error-box {
        background-color: #3D1F1F;
        padding: 15px;
        border-radius: 10px;
        border: 1px solid #FF6B6B;
        color: #FF6B6B;
    }
    div[data-testid="stSidebarNav"] {
        background-color: #1B263B;
    }
</style>
""", unsafe_allow_html=True)

with st.sidebar:
    st.markdown("""
    <div class="logo-container">
        <img src="{logo}" alt="TeresIA Logo">
    </div>
    """.format(logo=LOGO_URL), unsafe_allow_html=True)
    st.markdown("---")
    menu = st.radio("Menú", ["Inicio", "Extracción de Términos"])

if menu == "Inicio":
    st.markdown("""
    <div style="text-align: center; padding: 40px 20px;">
        <h1 style="color: #00B4D8 !important; font-size: 3em; margin-bottom: 20px;">Bienvenido a TeresIA</h1>
        <p style="font-size: 1.3em; line-height: 1.8;">
            Esto es una demo para los extractores de términos
        </p>
        <p style="font-size: 1.1em; color: #778DA9 !important; margin-top: 30px;">
            ¡Atención! Los servicios de extracción tardan un tiempo, en particular MDERank, ya que ambos servicios utilizan modelos de lenguaje sobre CPU.  
        </p>
    </div>
    """, unsafe_allow_html=True)

elif menu == "Extracción de Términos":
    st.title("Extracción de Términos")

    st.markdown("### Configuración")

    col1, col2 = st.columns([2, 1])

    with col1:
        texto_usuario = st.text_area(
            "Introduce el texto para extraer términos:",
            height=200,
            placeholder="Escribe o pega tu texto aquí..."
        )

    with col2:
        metodo = st.radio(
            "Selecciona el método:",
            ["AttentionRank", "MDERank"]
        )

        k_val = st.selectbox(
            "Número de términos a extraer:",
            options=[5, 10, 15],
            index=0
        )

    if st.button("Extraer Términos"):
        if not texto_usuario or len(texto_usuario.strip()) < 40:
            st.markdown("""
            <div class="error-box">
                ⚠️ El texto es muy corto. Introduce al menos 40 caracteres.
            </div>
            """, unsafe_allow_html=True)
        else:
            texto_escapado = html.escape(texto_usuario)

            if metodo == "AttentionRank":
                api_url = "https://termex.pcalleja.linkeddata.es/attentionrank"
            else:
                api_url = "https://termex.pcalleja.linkeddata.es/mderank"

            payload = {
                "doc": texto_escapado,
                "k_val": k_val
            }

            try:
                with st.spinner("Extrayendo términos..."):
                    response = requests.post(
                        api_url,
                        headers={
                            "accept": "application/json",
                            "Content-Type": "application/json"
                        },
                        json=payload,
                        timeout=120
                    )

                if response.status_code == 200:
                    resultado = response.json()
                    st.markdown("""
                    <div class="result-box">
                        <h3>Resultados - {}</h3>
                    </div>
                    """.format(metodo), unsafe_allow_html=True)

                    if isinstance(resultado, dict) and 'terms' in resultado:
                        terms = resultado['terms']
                    elif isinstance(resultado, list):
                        terms = resultado
                    else:
                        terms = resultado

                    if terms:
                        for i, term in enumerate(terms, 1):
                            st.markdown(f"**{i}.** {term}")

                        st.markdown("---")
                        st.markdown("### Texto Anotado")

                        texto_anotado = highlight_terms(texto_usuario, terms)
                        st.markdown(f"""
                        <div style="background-color: #1B263B; padding: 20px; border-radius: 10px; border: 1px solid #00B4D8; line-height: 1.8; font-size: 16px;">
                            {texto_anotado}
                        </div>
                        """, unsafe_allow_html=True)
                    else:
                        st.info("No se encontraron términos.")
                else:
                    st.markdown("""
                    <div class="error-box">
                        ⚠️ Error en la API: {} - {}
                    </div>
                    """.format(response.status_code, response.text), unsafe_allow_html=True)

            except requests.exceptions.RequestException as e:
                st.markdown("""
                <div class="error-box">
                    ⚠️ Error de conexión: {}
                </div>
                """.format(str(e)), unsafe_allow_html=True)

with st.sidebar:
    st.markdown("---")
    st.markdown("""
    <div style="text-align: center; opacity: 0.7;">
        <small>© 2025 Proyecto TeresIA</small>
    </div>
    """, unsafe_allow_html=True)
