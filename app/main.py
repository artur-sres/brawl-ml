import streamlit as st
from streamlit_option_menu import option_menu

from i18n import init_language, t, switch_language
from views.meta_view import render_meta
from views.draft_view import render_draft
# Importe as outras views assim que as refatorar: render_predictor, render_trainer

st.set_page_config(page_title="Brawl-ML Control", page_icon="🤖", layout="wide")
init_language()

with st.sidebar:
    selected_language = st.selectbox(
        "🌍 Language / Idioma", 
        options=['en', 'pt'], 
        format_func=lambda x: "English" if x == 'en' else "Português",
        index=0 if st.session_state['lang'] == 'en' else 1
    )
    
    if selected_language != st.session_state['lang']:
        switch_language(selected_language)
        st.rerun()

    st.markdown("---")

    page = option_menu(
        menu_title="Brawl-ML",
        options=[t("nav_meta"), t("nav_draft")], # Adicione as outras chaves aqui
        icons=["bar-chart", "crosshair"],
        menu_icon="robot", default_index=0, 
        styles={
            "container": {"padding": "5!important", "background-color": "transparent"},
            "icon": {"color": "#ffc107", "font-size": "20px"}, 
            "nav-link": {"font-size": "15px", "text-align": "left", "margin":"0px"},
            "nav-link-selected": {"background-color": "#2e7bcf"},
        }
    )

if page == t("nav_meta"): render_meta()
elif page == t("nav_draft"): render_draft()