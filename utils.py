import json
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, 'data')

# Ensure the data directory exists
if not os.path.exists(DATA_DIR):
    os.makedirs(DATA_DIR)

def read_json(file_name):
    file_path = os.path.join(DATA_DIR, file_name)
    
    # Ensure the file exists and has valid JSON content
    if not os.path.exists(file_path) or os.path.getsize(file_path) == 0:
        with open(file_path, 'w') as file:
            json.dump([], file)  # Initialize with an empty list if the file is empty
    
    with open(file_path, 'r') as file:
        return json.load(file)

def write_json(file_name, data):
    file_path = os.path.join(DATA_DIR, file_name)
    with open(file_path, 'w') as file:
        json.dump(data, file, indent=4)

def save_statistics(user_id, game_name, result, stats=None):
    data = read_json('score.json')

    # Find user and game entry
    user_entry = next((u for u in data if u['user_id'] == user_id and u['game'] == game_name), None)

    if user_entry:
        # Update game statistics
        if game_name == "Guess the Number" and stats:
            user_entry['statistics']['total_attempts'] += stats.get('total_attempts', 0)
            user_entry['statistics']['lowest_attempts'] = min(user_entry['statistics'].get('lowest_attempts', float('inf')), stats.get('lowest_attempts', float('inf')))
            user_entry['statistics']['highest_attempts'] = max(user_entry['statistics'].get('highest_attempts', 0), stats.get('highest_attempts', 0))
        elif game_name == "Rock Paper Scissors":
            user_entry['statistics'].setdefault('games_won', 0)
            user_entry['statistics'].setdefault('games_lost', 0)
            user_entry['statistics'].setdefault('games_tied', 0)
            user_entry['statistics'].setdefault('games_played', 0)
            
            if result == "win":
                user_entry['statistics']['games_won'] += 1
            elif result == "tie":
                user_entry['statistics']['games_tied'] += 1
            elif result == "lose":
                user_entry['statistics']['games_lost'] += 1
            user_entry['statistics']['games_played'] += 1
        elif game_name == "Math Quiz":
            user_entry['statistics'].setdefault('games_won', 0)
            user_entry['statistics'].setdefault('games_lost', 0)
            user_entry['statistics'].setdefault('games_played', 0)
            if result == "win":
                user_entry['statistics']['games_won'] += 1
            elif result == "lose":
                user_entry['statistics']['games_lost'] += 1
            user_entry['statistics']['games_played'] += 1
    else:
        # Create a new entry if not found
        new_entry = {
            "user_id": user_id,
            "game": game_name,
            "statistics": {}
        }
        if game_name == "Guess the Number" and stats:
            new_entry['statistics'] = {
                "total_attempts": stats.get('total_attempts', 0),
                "lowest_attempts": stats.get('lowest_attempts', float('inf')),
                "highest_attempts": stats.get('highest_attempts', 0),
                "games_played": 1
            }
        elif game_name == "Rock Paper Scissors":
            new_entry['statistics'] = {
                "games_won": 1 if result == "win" else 0,
                "games_lost": 1 if result == "lose" else 0,
                "games_tied": 1 if result == "tie" else 0,
                "games_played": 1
            }
        elif game_name == "Math Quiz":
            new_entry['statistics'] = {
                "games_won": 1 if result == "win" else 0,
                "games_lost": 1 if result == "lose" else 0,
                "games_played": 1
            }
        data.append(new_entry)

    # Write back the updated data to the JSON file
    write_json('score.json', data)



