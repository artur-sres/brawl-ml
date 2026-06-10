# brawl-match-predictor

Um pipeline completa ponta a ponta (Engenharia de Dados + Machine Learning) desenvolvido para prever resultados de partidas 3v3 no Brawl Stars, jogo da Supercell, com base na composição de equipes, mapas e outros diferenciais.

Este projeto é um ecossistema autônomo que coleta dados através de um *Crawler* em formato de rede (Busca em Largura), processa e nivela os dados relacionais, e treina um modelo preditivo.


## Arquitetura e Funcionalidades Técnicas

O projeto está estruturado em 4 fases sequenciais orquestradas por um menu interativo (`run.py`):

1. **Gestão de Banco de Dados SQLite:** - Arquitetura relacional isolada (`matches`, `players`, `match_players`).
   - Prevenção de redundância através de um algoritmo de *Hash Criptográfico*  gerado a partir das *tags* dos jogadores e do horário da partida.

2. **Crawler Engine:**
   - **Busca em Largura (BFS):** A engine lê o histórico de um jogador, descobre as *tags* de aliados/inimigos desconhecidos e os adiciona a uma fila de processamento, escalando a coleta de forma autônoma.
   - **Prevenção de Viés Temporal:** Implementação de um bloqueio lógico que restringe a coleta a *uma partida por mapa por usuário*. Isso impede que sessões repetitivas de jogo (*pushing*) viciem o modelo preditivo.
   - **Gestão de Rate Limits:** Tratamento automático de códigos HTTP 429 para evitar o banimento da chave de API.

3. **Pré-Processamento:**
   - Transformação do modelo relacional (linhas verticais) em uma matriz bidimensional horizontal (`dataset_brawl.csv`) utilizando `pandas`.
   - **Invariância Permutacional:** Ordenação alfabética interna para que a posição do jogador no *lobby* não afete o peso matemático da composição.
   - **Engenharia de Variáveis:** Cálculo de Vantagem Técnica (`delta_power` e `delta_trophies`), provando estatisticamente o peso do nível do jogador contra a composição pura.

4. **Machine Learning:**
   - Transição arquitetural para **Gradient Boosting Classifier** (Scikit-Learn) para mitigar a alta variância e o ruído gerados pela esparsidade da matriz de *Brawlers*.
   - Aplicação de *Multi-Hot Encoding* para as composições de equipe.
   - Exportação automática do modelo (`.pkl`) com auditoria do Top 10 de *Feature Importances* (Importância das Variáveis).

---

## Instalação e Configuração

### Pré-requisitos
- Python 3.9+
- Chave de API Oficial da Supercell (Brawl Stars API)

### 1. Clonar o Repositório
```bash
git clone [https://github.com/seu-usuario/brawl-ml-pipeline.git](https://github.com/seu-usuario/brawl-ml-pipeline.git)
cd brawl-ml-pipeline