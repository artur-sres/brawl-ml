import requests
import time
import hashlib
import os
from dotenv import load_dotenv
from data.database.db import get_connection

BASE_URL = "https://api.brawlstars.com/v1"

def generate_match_hash(battle_time, tag_list):
    """Generates a unique and deterministic ID for the match."""
    sorted_tags = sorted(tag_list)
    base_string = battle_time + "".join(sorted_tags)
    return hashlib.sha256(base_string.encode('utf-8')).hexdigest()

def run_collector():
    """Main function that orchestrates data collection from the API as a Crawler."""
    load_dotenv()
    TOKEN = os.getenv("BRAWL_API_TOKEN")
    if not TOKEN:
        print("Critical Error: BRAWL_API_TOKEN not found in the .env file.")
        return
        
    HEADERS = {"Authorization": f"Bearer {TOKEN}"}

    conn = get_connection()
    cur = conn.cursor()

    query_insert_match = """
        INSERT OR IGNORE INTO matches (match_hash, battle_time, mode, map, duration)
        VALUES (?, ?, ?, ?, ?)
    """
    # Note 'scanned = 0' marks new players as pending
    query_insert_player = """
        INSERT OR IGNORE INTO players (tag, name, scanned)
        VALUES (?, ?, 0)
    """
    query_insert_relation = """
        INSERT OR IGNORE INTO match_players 
        (match_hash, player_tag, team_id, brawler_name, power, trophies, result)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """

    # 1. Inject initial seeds if the database is completely empty
    seeds = ["#8QV90CYQ", "#8JJG8L8J9", "#90CV29899"]
    for seed in seeds:
        cur.execute(query_insert_player, (seed, "Unknown"))
    conn.commit()

    # 2. Safety Limit Configuration
    BATCH_LIMIT = 200
    processed_targets = 0

    print(f"Crawler Engine started. Limit set to {BATCH_LIMIT} targets.")

    # 3. Controlled Graph Execution (Crawler)
    try:
        while processed_targets < BATCH_LIMIT:
            # Strictly fetch 1 player that hasn't been processed yet (scanned = 0)
            cur.execute("SELECT tag FROM players WHERE scanned = 0 LIMIT 1")
            result = cur.fetchone()
            
            if not result:
                print("Processing queue is empty. All records have been analyzed.")
                break
                
            target_tag = result[0]
            print(f"[{time.strftime('%H:%M:%S')}] Processing target: {target_tag}")
            
            formatted_tag = target_tag.replace("#", "%23")
            url = f"{BASE_URL}/players/{formatted_tag}/battlelog"
            
            response = requests.get(url, headers=HEADERS)
            
            if response.status_code == 200:
                battlelog = response.json().get("items", [])
                
                # VARIANCE BARRIER: Tracks maps already extracted for THIS player
                seen_maps = set()
                
                for item in battlelog:
                    battle = item.get("battle", {})
                    
                    # Filter only 3v3 mode matches (which have 'teams')
                    if "teams" not in battle:
                        continue
                        
                    map_name = item.get("event", {}).get("map")
                    
                    # REDUNDANCY FILTER: If the map was already processed today for this target, skip the match
                    if map_name in seen_maps:
                        continue
                        
                    # Register the map as seen and proceed with extraction
                    seen_maps.add(map_name)
                    
                    battle_time = item.get("battleTime")
                    mode = battle.get("mode")
                    duration = battle.get("duration", 0)
                    
                    all_match_tags = []
                    for team in battle["teams"]:
                        for player in team:
                            all_match_tags.append(player["tag"])
                            
                    match_hash = generate_match_hash(battle_time, all_match_tags)
                    cur.execute(query_insert_match, (match_hash, battle_time, mode, map_name, duration))
                    
                    target_result = battle.get("result", "unknown")
                    target_team = None
                    
                    for tid, team in enumerate(battle["teams"]):
                        if any(p["tag"] == target_tag for p in team):
                            target_team = tid
                            break

                    for team_id, team in enumerate(battle["teams"]):
                        if team_id == target_team:
                            team_result = target_result
                        else:
                            if target_result == "victory":
                                team_result = "defeat"
                            elif target_result == "defeat":
                                team_result = "victory"
                            else:
                                team_result = target_result
                        
                        for player in team:
                            player_tag = player.get("tag")
                            
                            # EXPANSION HAPPENS HERE: Inserts new players into the queue
                            cur.execute(query_insert_player, (player_tag, player.get("name")))
                            
                            brawler = player.get("brawler", {})
                            relation_data = (
                                match_hash, player_tag, team_id, 
                                brawler.get("name"), brawler.get("power"), 
                                brawler.get("trophies"), team_result
                            )
                            cur.execute(query_insert_relation, relation_data)
                            
            elif response.status_code == 429:
                print("API rate limit exceeded. Pausing for 10 seconds.")
                time.sleep(10)
                continue
                
            else:
                print(f"Error {response.status_code} ignored for target {target_tag}.")
                
            # 4. Mark the current target as completed (scanned = 1) to avoid repeating it
            cur.execute("UPDATE players SET scanned = 1 WHERE tag = ?", (target_tag,))
            conn.commit()
            
            processed_targets += 1
            print(f"Progress: {processed_targets}/{BATCH_LIMIT} processed.\n")
            
            time.sleep(1)

        print(f"Batch of {BATCH_LIMIT} processed successfully. Safety stop.")

    except KeyboardInterrupt:
        # If you press Ctrl+C in the terminal, it falls here, saves progress, and exits cleanly
        print("\n[Warning] Manual interruption detected from user.")
        print("Saving current state and shutting down safely...")
        conn.commit()

    finally:
        # Final report and shutdown
        cur.execute("SELECT COUNT(*) FROM match_players")    
        print("Total records in match_players table:", cur.fetchone()[0])
        conn.close()
        print("Database connection closed.")