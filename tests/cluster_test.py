import sqlite3
conn = sqlite3.connect("data/storage/brawl_data.db")
import pandas as pd

# How many unique players are in the dataset
df_players = pd.read_sql_query("SELECT COUNT(*) as total FROM players", conn)
print("Jogadores únicos:", df_players['total'][0])

# Top 10 most frequent players in the dataset
df_top = pd.read_sql_query("""
    SELECT player_tag, COUNT(*) as aparicoes 
    FROM match_players 
    GROUP BY player_tag 
    ORDER BY aparicoes DESC 
    LIMIT 10
""", conn)
print(df_top)

conn.close()