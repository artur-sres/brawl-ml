import streamlit as st
import sqlite3
import pandas as pd
import sys
import os

# Garante o reconhecimento da raiz
diretorio_raiz = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
if diretorio_raiz not in sys.path:
    sys.path.append(diretorio_raiz)

from utils import localizar_arquivo, carregar_dados_banco

@st.cache_data
def extrair_estatisticas_mapa(modo, mapa):
    """Consulta o SQLite para obter o número de escolhas e vitórias por Brawler num mapa específico."""
    caminho_db = localizar_arquivo('brawl_data.db') or localizar_arquivo('raw_events.sqlite')
    if not caminho_db:
        return pd.DataFrame()

    conn = sqlite3.connect(caminho_db)
    
    # A Query matemática: Conta presenças e soma vitórias
    query = """
    SELECT 
        mp.brawler_name AS Brawler,
        COUNT(mp.match_hash) AS Total_Picks,
        SUM(CASE WHEN mp.result = 'victory' THEN 1 ELSE 0 END) AS Vitorias
    FROM match_players mp
    JOIN matches m ON mp.match_hash = m.match_hash
    WHERE m.mode = ? AND m.map = ?
    GROUP BY mp.brawler_name
    ORDER BY Total_Picks DESC
    """
    
    df = pd.read_sql_query(query, conn, params=(modo, mapa))
    conn.close()

    # Cálculo da Taxa de Vitória (Win Rate)
    if not df.empty:
        df['Win_Rate'] = (df['Vitorias'] / df['Total_Picks']) * 100
        # Filtra Brawlers com menos de 3 partidas para não distorcer estatísticas (ex: 1 jogo / 1 vitória = 100%)
        df = df[df['Total_Picks'] >= 3].copy()
        
    return df

def renderizar_meta():
    st.title("📊 Análise de Meta (Estatísticas)")
    st.markdown("Descubra os Brawlers mais jogados e mais eficientes com base no seu histórico real.")

    modos, mapas_por_modo, _ = carregar_dados_banco()

    if not modos:
        st.error("Base de dados vazia ou não encontrada.")
        st.stop()

    # --- SELETORES DE CONTEXTO ---
    st.header("🔍 Filtrar Cenário")
    col1, col2 = st.columns(2)
    with col1:
        modo_selecionado = st.selectbox("Modo de Jogo:", modos, key="meta_modo")
    with col2:
        mapa_selecionado = st.selectbox("Mapa:", mapas_por_modo.get(modo_selecionado, []), key="meta_mapa")

    caminho_imagem_mapa = localizar_arquivo(f"{mapa_selecionado.replace(' ', '_')}.png")
    if caminho_imagem_mapa:
        st.image(caminho_imagem_mapa, caption=mapa_selecionado, use_container_width=True)
    else:
        st.info(f"💡 Imagem do mapa não encontrada: {mapa_selecionado}.png")
    st.markdown("---")
    
    # Extrai os dados
    df_stats = extrair_estatisticas_mapa(modo_selecionado, mapa_selecionado)

    if df_stats.empty:
        st.warning(f"⚠️ Não existem partidas suficientes guardadas para o mapa '{mapa_selecionado}'. Rode o Crawler mais vezes.")
        return

    # --- PAINEL DE MÉTRICAS (TOP 3 PICKS) ---
    st.subheader(f"🏆 Top 3 Picks: {mapa_selecionado}")
    top_3 = df_stats.head(3)
    cols = st.columns(3)
    
    for i, (_, row) in enumerate(top_3.iterrows()):
        brawler = row['Brawler']
        wr = row['Win_Rate']
        
        with cols[i]:
            caminho_img = localizar_arquivo(f"{brawler.replace(' ', '_')}.webp")
            
            # CRIAMOS UMA COLUNA INTERNA PARA FORÇAR O CENTRAMENTO
            # A técnica de 'st.columns([1, 2, 1])' cria colunas laterais vazias para centrar a do meio
            _, c_img, _ = st.columns([1, 2, 1])
            
            if caminho_img:
                with c_img:
                    st.image(caminho_img, use_container_width=True)
            
            # Texto centralizado usando HTML simples
            st.markdown(f"""
                <div style='text-align: center;'>
                    <b>{brawler}</b><br>
                    <span style='font-size: 0.9em;'>{wr:.1f}% WR</span>
                </div>
            """, unsafe_allow_html=True)

    st.markdown("---")

    # --- TABELAS GERAIS ---
        # Tabela em cima
    st.subheader("📋 Tabela Completa")
    st.dataframe(
        df_stats,
        column_config={
            "Brawler": st.column_config.TextColumn("Brawler"),
            "Total_Picks": st.column_config.NumberColumn("Partidas", format="%d"),
            "Vitorias": None,
            "Win_Rate": st.column_config.ProgressColumn("Taxa de Vitória", format="%.1f%%", min_value=0, max_value=100),
        },
        hide_index=True,
        use_container_width=True # Garante largura total
    )

    # Gráfico em baixo (Horizontal)
    st.subheader("📈 Frequência de Escolha")
    # Para o gráfico ficar horizontal, basta usar o st.bar_chart com os dados ordenados 
    # e o Streamlit assume o sentido da série.
    df_chart = df_stats[['Brawler', 'Total_Picks']].set_index('Brawler').head(10)
    # Inverte o dataframe para o gráfico aparecer com os nomes na vertical (barra horizontal)
    st.bar_chart(df_chart.sort_values(by='Total_Picks', ascending=True), color="#2e7bcf")