import streamlit as st
import sys
import os

root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
if root_dir not in sys.path:
    sys.path.append(root_dir)

from utils import locate_file, load_database_data, load_model
from data.prediction.predictor import calculate_static_probability, recommend_draft_brawlers
from i18n import t

def render_draft():
    st.title(f"🎯 {t('draft_title')}")
    st.markdown(t("draft_subtitle"))

    modes, maps_by_mode, valid_brawlers = load_database_data()
    model, training_columns = load_model()

    if not model or not modes:
        st.error(t("error_missing_model"))
        st.stop()

    st.header(f"🗺️ {t('scenario')}")
    col_mode, col_map = st.columns(2)
    with col_mode:
        selected_mode = st.selectbox(t("game_mode"), modes, key="draft_mode")
    with col_map:
        selected_map = st.selectbox(t("map"), maps_by_mode.get(selected_mode, []), key="draft_map")

    brawler_options = [f"--- {t('empty')} ---"] + valid_brawlers

    st.markdown("---")
    st.header(f"⚔️ {t('draft_board')}")
    col_t0, col_t1 = st.columns(2)

    with col_t0:
        st.subheader(f"🔵 {t('allies')}")
        a1 = st.selectbox("Slot 1:", brawler_options, index=0, key="a1")
        a2 = st.selectbox("Slot 2:", brawler_options, index=0, key="a2")
        a3 = st.selectbox("Slot 3:", brawler_options, index=0, key="a3")

    with col_t1:
        st.subheader(f"🔴 {t('enemies')}")
        e1 = st.selectbox("Slot 1:", brawler_options, index=0, key="e1")
        e2 = st.selectbox("Slot 2:", brawler_options, index=0, key="e2")
        e3 = st.selectbox("Slot 3:", brawler_options, index=0, key="e3")

    selected_allies = [b for b in [a1, a2, a3] if "---" not in b]
    selected_enemies = [b for b in [e1, e2, e3] if "---" not in b]
    all_selected = selected_allies + selected_enemies

    if len(set(all_selected)) < len(all_selected):
        st.error(f"⚠️ {t('error_duplicate_brawlers')}")
        st.stop()

    st.markdown("---")
    
    if len(selected_allies) == 3 and len(selected_enemies) == 3:
        st.subheader(f"📊 {t('final_analysis')}")
        prob_defeat, prob_victory = calculate_static_probability(
            model, training_columns, selected_mode, selected_map, selected_allies, selected_enemies
        )
        st.metric(label=t("win_chances"), value=f"{prob_victory:.1f}%")
        st.progress(int(prob_victory))
        
    elif len(selected_allies) < 3:
        st.subheader(f"💡 {t('team_recommendations')}")
        st.caption(t("testing_synergies"))
        
        top_5 = recommend_draft_brawlers(
            model, training_columns, selected_mode, selected_map, 
            selected_allies, selected_enemies, valid_brawlers
        )
        
        cols = st.columns(5)
        for i, (brawler, prob) in enumerate(top_5):
            with cols[i]:
                img_path = locate_file(f"{brawler.replace(' ', '_')}.webp")
                if img_path:
                    st.image(img_path, width="stretch")
                st.markdown(f"<div style='text-align: center;'><b>{brawler}</b><br>{prob:.1f}%</div>", unsafe_allow_html=True)