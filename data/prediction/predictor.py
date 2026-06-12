import pandas as pd

def calculate_static_probability(model, training_columns, mode, map_name, team_0, team_1):
    """Calculates the probability for a complete 3v3 match."""
    input_data = pd.DataFrame(0, index=[0], columns=training_columns)
    
    if f'mode_{mode}' in training_columns: input_data.at[0, f'mode_{mode}'] = 1
    if f'map_{map_name}' in training_columns: input_data.at[0, f'map_{map_name}'] = 1
    
    for b in team_0:
        if f't0_{b}' in training_columns: input_data.at[0, f't0_{b}'] = 1
    for b in team_1:
        if f't1_{b}' in training_columns: input_data.at[0, f't1_{b}'] = 1
        
    probabilities = model.predict_proba(input_data)[0]
    return probabilities[0] * 100, probabilities[1] * 100

def recommend_draft_brawlers(model, training_columns, mode, map_name, allies, enemies, valid_brawlers):
    """Executes vectorized simulations to fill an empty slot in the allied team."""
    selected_brawlers = allies + enemies
    candidates = [b for b in valid_brawlers if b not in selected_brawlers]
    
    if not candidates: return []

    base_df = pd.DataFrame(0, index=[0], columns=training_columns)
    if f'mode_{mode}' in training_columns: base_df.at[0, f'mode_{mode}'] = 1
    if f'map_{map_name}' in training_columns: base_df.at[0, f'map_{map_name}'] = 1
    
    for b in allies:
        if f't0_{b}' in training_columns: base_df.at[0, f't0_{b}'] = 1
    for b in enemies:
        if f't1_{b}' in training_columns: base_df.at[0, f't1_{b}'] = 1

    simulation_df = pd.concat([base_df] * len(candidates), ignore_index=True)
    
    for i, candidate in enumerate(candidates):
        if f't0_{candidate}' in training_columns:
            simulation_df.at[i, f't0_{candidate}'] = 1
            
    probabilities = model.predict_proba(simulation_df)
    
    results = []
    for i, candidate in enumerate(candidates):
        win_prob = probabilities[i][1] * 100
        results.append((candidate, win_prob))
        
    results.sort(key=lambda x: x[1], reverse=True)
    return results[:5]