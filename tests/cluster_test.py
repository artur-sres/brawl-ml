import sqlite3
conn = sqlite3.connect("brawl_data.db")  # ajuste o caminho se necessário
import pandas as pd

# Quantos jogadores únicos existem
df_players = pd.read_sql_query("SELECT COUNT(*) as total FROM players", conn)
print("Jogadores únicos:", df_players['total'][0])

# Top 10 jogadores que mais aparecem em match_players
df_top = pd.read_sql_query("""
    SELECT player_tag, COUNT(*) as aparicoes 
    FROM match_players 
    GROUP BY player_tag 
    ORDER BY aparicoes DESC 
    LIMIT 10
""", conn)
print(df_top)

conn.close()