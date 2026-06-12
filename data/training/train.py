import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import GradientBoostingClassifier
from sklearn.metrics import accuracy_score, classification_report
import joblib
import os

def train_model():
    print("Loading dataset...")
    current_dir = os.path.dirname(os.path.abspath(__file__))
    csv_path = os.path.abspath(os.path.join(current_dir, "..", "..", "data", "storage", "dataset_brawl.csv"))
    
    try:
        df = pd.read_csv(csv_path)
    except FileNotFoundError:
        print(f"Critical Error: File not found at {csv_path}")
        return

    print(f"Dataset loaded with {len(df)} matches. Starting matrix transformation...")

    # 1. Transform Basic Categorical Variables
    df_encoded = pd.get_dummies(df, columns=['mode', 'map'])

    # 2. Team Graph Transformation (Multi-Hot Encoding)
    print("Flattening Brawler order (Permutational Invariance)...")
    all_brawlers = set(df['t0_brawler_1']).union(
        df['t0_brawler_2'], df['t0_brawler_3'],
        df['t1_brawler_1'], df['t1_brawler_2'], df['t1_brawler_3']
    )

    new_columns = {}
    for brawler in all_brawlers:
        new_columns[f't0_{brawler}'] = 0
        new_columns[f't1_{brawler}'] = 0

    df_new = pd.DataFrame(new_columns, index=df_encoded.index)
    df_encoded = pd.concat([df_encoded, df_new], axis=1)

    for i in range(1, 4):
        for brawler in all_brawlers:
            df_encoded.loc[df[f't0_brawler_{i}'] == brawler, f't0_{brawler}'] = 1
            df_encoded.loc[df[f't1_brawler_{i}'] == brawler, f't1_{brawler}'] = 1

    text_columns = ['match_hash', 't0_brawler_1', 't0_brawler_2', 't0_brawler_3',
                    't1_brawler_1', 't1_brawler_2', 't1_brawler_3']
    df_encoded = df_encoded.drop(columns=text_columns)

    # 3. Define Target and Features
    X = df_encoded.drop(columns=['target'])
    y = df_encoded['target']

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    print("Starting Gradient Boosting Algorithm training...")
    model = GradientBoostingClassifier(n_estimators=200, learning_rate=0.05, max_depth=4, random_state=42)
    model.fit(X_train, y_train)

    # 4. Mathematical Evaluation
    predictions = model.predict(X_test)
    accuracy = accuracy_score(y_test, predictions)

    print("\n================ RESULTS ================")
    print(f"Base Accuracy: {accuracy * 100:.2f}%")
    print(classification_report(y_test, predictions, target_names=['Team 0 Defeat', 'Team 0 Victory']))
    print("=========================================")
    
    # 5. Save AI state
    root_dir = os.path.abspath(os.path.join(current_dir, "..", ".."))
    model_path = os.path.join(root_dir, 'data', 'storage', 'model.pkl')
    columns_path = os.path.join(root_dir, 'data', 'storage', 'columns.pkl')
    
    joblib.dump(model, model_path)
    joblib.dump(X.columns.tolist(), columns_path)
    print(f"\nMathematical model exported to: {model_path}")

if __name__ == "__main__":
    train_model()