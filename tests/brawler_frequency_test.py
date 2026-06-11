import pandas as pd
df = pd.read_csv("dataset_brawl.csv")

# Quantas vezes cada brawler aparece no total (t0 + t1)
from collections import Counter
contagem = Counter()
for col in ['t0_brawler_1','t0_brawler_2','t0_brawler_3','t1_brawler_1','t1_brawler_2','t1_brawler_3']:
    contagem.update(df[col])

print(pd.Series(contagem).sort_values(ascending=False).head(15))
print("\nTotal de partidas:", len(df))
print("Brawlers únicos vistos:", len(contagem))