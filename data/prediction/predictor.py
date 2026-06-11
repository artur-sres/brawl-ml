import pandas as pd
import joblib
import os

def localizar_arquivo(nome_arquivo):
    """Varre todo o projeto autonomamente à procura do arquivo."""
    diretorio_raiz = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
    for root, dirs, files in os.walk(diretorio_raiz):
        if nome_arquivo in files:
            return os.path.join(root, nome_arquivo)
    return None

def fazer_previsao(equipa_0, equipa_1, modo, mapa, delta_power, delta_trophies):
    # 1. Busca Universal dos Artefatos (Procura os nomes antigos e os novos)
    caminho_modelo = localizar_arquivo('modelo_brawl.pkl') or localizar_arquivo('classifier_gb_v1.pkl')
    caminho_colunas = localizar_arquivo('colunas_brawl.pkl') or localizar_arquivo('feature_names_v1.pkl')
    
    if not caminho_modelo or not caminho_colunas:
        print("\n[Erro Crítico] Arquivos .pkl não encontrados em nenhuma pasta do projeto.")
        print("Certifique-se de que rodou a Opção 4 para treinar a IA pelo menos uma vez.")
        return

    # Carrega os cérebros da IA a partir dos caminhos reais que encontrou
    modelo = joblib.load(caminho_modelo)
    colunas_treino = joblib.load(caminho_colunas)

    # 2. Reconstrução da Matriz de Entrada (Zerar tudo)
    entrada = pd.DataFrame(0, index=[0], columns=colunas_treino)

    # 3. Preenchimento das Variáveis Categóricas Básicas
    coluna_modo = f'mode_{modo}'
    if coluna_modo in colunas_treino:
        entrada.at[0, coluna_modo] = 1

    coluna_mapa = f'map_{mapa}'
    if coluna_mapa in colunas_treino:
        entrada.at[0, coluna_mapa] = 1

    # 4. Preenchimento das Variáveis Contínuas
    if 'delta_power' in colunas_treino:
        entrada.at[0, 'delta_power'] = delta_power
    if 'delta_trophies' in colunas_treino:
        entrada.at[0, 'delta_trophies'] = delta_trophies

    # 5. Preenchimento do Multi-Hot Encoding para os Brawlers
    for brawler in equipa_0:
        col = f't0_{brawler.upper()}'
        if col in colunas_treino:
            entrada.at[0, col] = 1
            
    for brawler in equipa_1:
        col = f't1_{brawler.upper()}'
        if col in colunas_treino:
            entrada.at[0, col] = 1

    # 6. Execução Matemática (Inferência)
    probabilidades = modelo.predict_proba(entrada)[0]
    
    prob_derrota = probabilidades[0] * 100
    prob_vitoria = probabilidades[1] * 100

    print("\n" + "="*45)
    print(" PREVISÃO DO MOTOR DE INTELIGÊNCIA ARTIFICIAL ")
    print("="*45)
    print(f"Probabilidade de Vitória (Sua Equipe): {prob_vitoria:.2f}%")
    print(f"Probabilidade de Derrota (Sua Equipe): {prob_derrota:.2f}%")
    
    if prob_vitoria > 55:
        print("\n>> Veredito: VANTAGEM SÓLIDA PARA A SUA EQUIPE")
    elif prob_derrota > 55:
        print("\n>> Veredito: VANTAGEM SÓLIDA PARA A EQUIPE INIMIGA")
    else:
        print("\n>> Veredito: PARTIDA ALTAMENTE EQUILIBRADA (Risco Máximo)")
    print("="*45)

def iniciar_interface_previsao():
    print("\n--- SIMULADOR DE PARTIDA (MODO RÁPIDO) ---")
    print("Introduza os Brawlers separados por vírgula (Ex: Shelly, Colt, Bull)")
    
    t0_input = input("Sua Equipe (Aliados): ").split(',')
    t1_input = input("Equipe Inimiga (Adversários): ").split(',')
    
    t0_brawlers = [b.strip() for b in t0_input]
    t1_brawlers = [b.strip() for b in t1_input]
    
    modo = input("Modo de Jogo (Ex: Brawl Ball): ").strip()
    mapa = input("Mapa (Ex: Super Beach): ").strip()
    
    # Princípio do Delta Zero
    delta_power_neutro = 0.0
    delta_trophies_neutro = 0.0

    print("\n[Sistema] Analisando sinergia e vantagem de mapa...")
    
    fazer_previsao(
        t0_brawlers, 
        t1_brawlers, 
        modo, 
        mapa, 
        delta_power_neutro, 
        delta_trophies_neutro
    )

if __name__ == "__main__":
    iniciar_interface_previsao()