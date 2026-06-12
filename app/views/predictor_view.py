import streamlit as st
import sys
import os

root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
if root_dir not in sys.path:
    sys.path.append(root_dir)

from utils import locate_file, load_database_data, load_model
from data.prediction.predictor import calculate_static_probability
from i18n import t

def render_predictor():
    st.title(t("predictor_title"))
    st.markdown(t("predictor_subtitle"))

    modes, maps_by_mode, valid_brawlers = load_database_data()
    model, training_columns = load_model()

    if not modes:
        st.error(t("error_missing_db"))
        st.stop()

    if not model:
        st.error(t("error_missing_artifacts"))
        st.stop()

    # 1. SCENARIO SECTION
    st.header(f"🗺️ {t('scenario')}")
    col_mode, col_map = st.columns(2)

    with col_mode:
        selected_mode = st.selectbox(t("game_mode"), modes)

    with col_map:
        available_maps = maps_by_mode.get(selected_mode, [])
        selected_map = st.selectbox(t("map"), available_maps)

    map_img_path = locate_file(f"{selected_map.replace(' ', '_')}.png")
    if map_img_path:
        st.image(map_img_path, caption=selected_map, width="stretch")
    else:
        st.info(f"💡 {selected_map}.png not found.")

    # 2. TEAMS SECTION
    st.header(f"⚔️ {t('compositions')}")
    col_t0, col_t1 = st.columns(2)

    with col_t0:
        st.subheader(f"🔵 {t('your_team')}")
        t0_b1 = st.selectbox(t("ally").format(1), valid_brawlers, index=0)
        t0_b2 = st.selectbox(t("ally").format(2), valid_brawlers, index=1)
        t0_b3 = st.selectbox(t("ally").format(3), valid_brawlers, index=2)
        
        cols_img_t0 = st.columns(3)
        for i, brawler in enumerate([t0_b1, t0_b2, t0_b3]):
            brawler_path = locate_file(f"{brawler.replace(' ', '_')}.webp")
            if brawler_path:
                cols_img_t0[i].image(brawler_path, width="stretch")
            else:
                no_photo_text = t("no_photo").format(brawler)
                cols_img_t0[i].markdown(f"<div style='text-align: center; font-size: 10px; color: gray;'>{no_photo_text}</div>", unsafe_allow_html=True)

    with col_t1:
        st.subheader(f"🔴 {t('enemy_team')}")
        t1_b1 = st.selectbox(t("opponent").format(1), valid_brawlers, index=3)
        t1_b2 = st.selectbox(t("opponent").format(2), valid_brawlers, index=4)
        t1_b3 = st.selectbox(t("opponent").format(3), valid_brawlers, index=5)
        
        cols_img_t1 = st.columns(3)
        for i, brawler in enumerate([t1_b1, t1_b2, t1_b3]):
            brawler_path = locate_file(f"{brawler.replace(' ', '_')}.webp")
            if brawler_path:
                cols_img_t1[i].image(brawler_path, width="stretch")
            else:
                no_photo_text = t("no_photo").format(brawler)
                cols_img_t1[i].markdown(f"<div style='text-align: center; font-size: 10px; color: gray;'>{no_photo_text}</div>", unsafe_allow_html=True)

    # 3. INFERENCE ENGINE
    st.markdown("---")
    if st.button(f"🧠 {t('calculate_win_probability')}", width="stretch"):
        team_0 = [t0_b1, t0_b2, t0_b3]
        team_1 = [t1_b1, t1_b2, t1_b3]
        
        if len(set(team_0)) < 3 or len(set(team_1)) < 3:
            st.warning(f"⚠️ {t('error_duplicate_brawlers')}")
        else:
            # Clean delegation to the predictor logic
            prob_defeat, prob_victory = calculate_static_probability(
                model, training_columns, selected_mode, selected_map, team_0, team_1
            )
            
            st.subheader(f"📊 {t('analysis_result')}")
            st.metric(label=t("win_chances"), value=f"{prob_victory:.1f}%")
            st.progress(int(prob_victory))
            
            if prob_victory > 55:
                st.success(t("verdict_superior"))
            elif prob_defeat > 55:
                st.error(t("verdict_disadvantage"))
            else:
                st.warning(t("verdict_balanced"))