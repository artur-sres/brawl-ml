import streamlit as st
import sqlite3
import os
import sys

root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
if root_dir not in sys.path:
    sys.path.append(root_dir)

from data.collector.collector import run_collector 
from data.preprocessing.dataset_builder import build_dataset 
from data.training.train import train_model

from utils import locate_file
from i18n import t

def get_db_statistics():
    """Queries the database to return match and brawler counts."""
    db_path = locate_file('brawl_data.db') or locate_file('raw_events.sqlite')
    
    if not db_path:
        return 0, 0
    
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    
    try:
        cur.execute("SELECT COUNT(DISTINCT match_hash) FROM matches")
        total_matches = cur.fetchone()[0]
        
        cur.execute("SELECT COUNT(DISTINCT brawler_name) FROM match_players")
        total_brawlers = cur.fetchone()[0]
    except Exception as e:
        print(f"Database read error: {e}")
        total_matches, total_brawlers = 0, 0
        
    conn.close()
    return total_matches, total_brawlers


def render_trainer():
    st.title(t("trainer_title"))
    st.write(t("trainer_subtitle"))
    
    total_matches, total_brawlers = get_db_statistics()
    
    st.markdown("---")
    st.subheader(f"📊 {t('db_health')}")
    col1, col2 = st.columns(2)
    col1.metric(t("unique_matches"), total_matches)
    col2.metric(t("mapped_brawlers"), total_brawlers)
    
    if total_matches < 7000:
        st.warning(t("critical_volume_warning"))
    else:
        st.success(t("ideal_volume_success"))
    
    st.markdown("---")
    st.subheader(f"🛠️ {t('mlops_operations')}")
    
    if st.button(t("run_crawler_btn"), width="stretch"):
        with st.spinner(t("crawler_spinner")):
            try:
                run_collector()
                st.success(t("crawler_success"))
            except Exception as e:
                st.error(t("crawler_error").format(e))
                
    if st.button(t("train_model_btn"), width="stretch"):
        with st.spinner(t("train_step1_spinner")):
            try:
                build_dataset() 
                
                with st.spinner(t("train_step2_spinner")):
                    train_model()
                    
                st.success(t("train_success"))
                st.info(t("train_info"))
            except Exception as e:
                st.error(t("train_error").format(e))