import streamlit as st
import pandas as pd
import joblib
import sqlite3
import os

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(page_title="Brawl-ML Predictor", page_icon="🤖", layout="centered")

# --- FUNÇÃO RADAR (Busca Universal) ---
def localizar_arquivo(nome_arquivo):
    """Varre todo o projeto autonomamente à procura do arquivo."""
    # Pega o diretório onde o testing.py está rodando
    diretorio_raiz = os.path.abspath(os.path.dirname(__file__))
    for root, dirs, files in os.walk(diretorio_raiz):
        if nome_arquivo in files:
            return os.path.join(root, nome_arquivo)
    return None

# --- FUNÇÕES DE BUSCA E CACHE ---
@st.cache_data
def carregar_dados_banco():
    # Usa o radar para achar o banco, seja o nome antigo ou o novo
    caminho_db = localizar_arquivo('brawl_data.db') or localizar_arquivo('raw_events.sqlite')
    
    if not caminho_db:
        return [], {}, []

    conn = sqlite3.connect(caminho_db)
    cur = conn.cursor()

    cur.execute("SELECT DISTINCT mode FROM matches")
    modos = [row[0] for row in cur.fetchall()]

    mapas_por_modo = {}
    for modo in modos:
        cur.execute("SELECT DISTINCT map FROM matches WHERE mode = ?", (modo,))
        mapas_por_modo[modo] = [row[0] for row in cur.fetchall()]

    cur.execute("SELECT DISTINCT brawler_name FROM match_players")
    brawlers_validos = sorted([row[0].upper() for row in cur.fetchall()])

    conn.close()
    return modos, mapas_por_modo, brawlers_validos

@st.cache_resource
def carregar_modelo():
    # Usa o radar para achar os modelos, com o nome velho ou o novo padrão MLOps
    caminho_modelo = localizar_arquivo('modelo_brawl.pkl') or localizar_arquivo('classifier_gb_v1.pkl')
    caminho_colunas = localizar_arquivo('colunas_brawl.pkl') or localizar_arquivo('feature_names_v1.pkl')
    
    if caminho_modelo and caminho_colunas:
        modelo = joblib.load(caminho_modelo)
        colunas = joblib.load(caminho_colunas)
        return modelo, colunas
    
    return None, None

# --- CARREGAMENTO DE DADOS (Execução) ---
modos, mapas_por_modo, brawlers_validos = carregar_dados_banco()
modelo, colunas_treino = carregar_modelo()

# --- CARREGAMENTO DE DADOS ---
modos, mapas_por_modo, brawlers_validos = carregar_dados_banco()
modelo, colunas_treino = carregar_modelo()

# --- INTERFACE VISUAL ---
st.title("🤖 Previsor de Partidas 3v3")
st.markdown("Analise composições do **Brawl Stars** com Inteligência Artificial.")

if not modos:
    st.error(" Banco de dados (brawl_data.db) não encontrado. Rode o Crawler primeiro.")
    st.stop()

if not modelo:
    st.error(" Artefatos da IA (.pkl) não encontrados. Treine o modelo primeiro.")
    st.stop()

# 1. SEÇÃO DE MAPA E MODO
st.header("🗺️ Cenário")
col_modo, col_mapa = st.columns(2)

with col_modo:
    modo_selecionado = st.selectbox("Modo de Jogo:", modos)

with col_mapa:
    mapas_disponiveis = mapas_por_modo.get(modo_selecionado, [])
    mapa_selecionado = st.selectbox("Mapa:", mapas_disponiveis)

# Lógica da Imagem do Mapa
caminho_imagem = f"assets/maps/{mapa_selecionado.replace(' ', '_')}.png"
if os.path.exists(caminho_imagem):
    st.image(caminho_imagem, caption=mapa_selecionado, use_container_width=True)
else:
    st.info(f"💡 Dica de Design: Salve uma imagem do mapa em `{caminho_imagem}` para ela aparecer aqui.")

# 2. SEÇÃO DE EQUIPES
st.header("⚔️ Composições")
col_t0, col_t1 = st.columns(2)

with col_t0:
    st.subheader("🔵 Sua Equipe")
    t0_b1 = st.selectbox("Aliado 1:", brawlers_validos, index=0)
    t0_b2 = st.selectbox("Aliado 2:", brawlers_validos, index=1)
    t0_b3 = st.selectbox("Aliado 3:", brawlers_validos, index=2)

with col_t1:
    st.subheader("🔴 Equipe Inimiga")
    t1_b1 = st.selectbox("Adversário 1:", brawlers_validos, index=3)
    t1_b2 = st.selectbox("Adversário 2:", brawlers_validos, index=4)
    t1_b3 = st.selectbox("Adversário 3:", brawlers_validos, index=5)

# 3. MOTOR DE INFERÊNCIA
st.markdown("---")
if st.button("🧠 Calcular Probabilidade de Vitória", use_container_width=True):
    
    # Validação de Brawlers Repetidos na mesma equipe
    equipe_0 = [t0_b1, t0_b2, t0_b3]
    equipe_1 = [t1_b1, t1_b2, t1_b3]
    
    if len(set(equipe_0)) < 3 or len(set(equipe_1)) < 3:
        st.warning("⚠️ O Brawl Stars não permite Brawlers repetidos na mesma equipe. Ajuste a composição.")
    else:
        # Cria a matriz vazia
        entrada = pd.DataFrame(0, index=[0], columns=colunas_treino)
        
        # Preenche Variáveis Categóricas
        if f'mode_{modo_selecionado}' in colunas_treino: entrada.at[0, f'mode_{modo_selecionado}'] = 1
        if f'map_{mapa_selecionado}' in colunas_treino: entrada.at[0, f'map_{mapa_selecionado}'] = 1
        
        # Injeta Equilíbrio de Nível Matemático (Delta Zero)
        if 'delta_power' in colunas_treino: entrada.at[0, 'delta_power'] = 0.0
        if 'delta_trophies' in colunas_treino: entrada.at[0, 'delta_trophies'] = 0.0
        
        # Preenche Brawlers
        for b in equipe_0:
            if f't0_{b}' in colunas_treino: entrada.at[0, f't0_{b}'] = 1
        for b in equipe_1:
            if f't1_{b}' in colunas_treino: entrada.at[0, f't1_{b}'] = 1
            
        # Calcula a probabilidade
        probabilidades = modelo.predict_proba(entrada)[0]
        prob_derrota = probabilidades[0] * 100
        prob_vitoria = probabilidades[1] * 100
        
        # Exibe o resultado com barras de progresso visuais
        st.subheader("📊 Resultado da Análise")
        st.metric(label="Chances de Vitória (Sua Equipe)", value=f"{prob_vitoria:.1f}%")
        st.progress(int(prob_vitoria))
        
        if prob_vitoria > 55:
            st.success("Veredito: Composição superior. Vantagem sólida para a Sua Equipe!")
        elif prob_derrota > 55:
            st.error("Veredito: Desvantagem estrutural. A Equipe Inimiga tem controle da partida.")
        else:
            st.warning("Veredito: Partida altamente equilibrada. O resultado dependerá puramente da habilidade dos jogadores.")