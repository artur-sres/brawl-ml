import streamlit as st
from streamlit_option_menu import option_menu
from views.predictor_view import renderizar_previsor
from views.trainer_view import renderizar_treinamento
from views.draft_view import renderizar_draft
from views.meta_view import renderizar_meta


st.set_page_config(page_title="Brawl-ML Control", page_icon="🤖", layout="centered")

st.markdown("""
<style>
[data-testid="stSidebar"] {
    width: 300px !important;
    min-width: 400px !important;
    max-width: 400px !important;
}
</style>
""", unsafe_allow_html=True)

# --- BARRA DE NAVEGAÇÃO LATERAL (ESTILIZADA) ---
with st.sidebar:
    pagina = option_menu(
        menu_title="Brawl-ML",       # Título do menu
        options=["Meta", "Chance de Vitória", "Treino & Logs", "Taxa de Vitória por Brawler", "Taxa de Vitória por Mapa", "Taxa de Vitória por Composição", "Simular Draft", "Rank de Picks por Mapa"], # Opções
        icons=["controller", "cpu", "bar-chart", "map", "people", "trophy", "award"], # Ícones do Bootstrap (https://icons.getbootstrap.com/)
        menu_icon="robot",           # Ícone principal do menu
        default_index=0,             # Página que abre por defeito
        styles={
            "container": {"padding": "5!important", "background-color": "transparent"},
            "icon": {"color": "#ffc107", "font-size": "20px"}, 
            "nav-link": {"font-size": "15px", "text-align": "left", "margin":"0px", "--hover-color": "rgba(255, 255, 255, 0.05)"},
            "nav-link-selected": {"background-color": "#2e7bcf"},
        }
    )

# --- LÓGICA DE NAVEGAÇÃO ---
if pagina == "Meta":
    renderizar_meta()
elif pagina == "Chance de Vitória":
    renderizar_previsor()

elif pagina == "Treino & Logs":
    renderizar_treinamento()

elif pagina == "Simular Draft":
    renderizar_draft()