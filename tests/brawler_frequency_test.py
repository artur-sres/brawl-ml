import pandas as pd
df = pd.read_csv("data/storage/dataset_brawl.csv")

# How many times each brawler appears in the dataset
from collections import Counter
counter = Counter()
for col in ['t0_brawler_1','t0_brawler_2','t0_brawler_3','t1_brawler_1','t1_brawler_2','t1_brawler_3']:
    counter.update(df[col])

print(pd.Series(counter).sort_values(ascending=False).head(15))
print("\nTotal of matches:", len(df))
print("Unique brawlers seen:", len(counter))