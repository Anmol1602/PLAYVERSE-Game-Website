# games.py

from flask import Blueprint

# Create a blueprint for the games
games_bp = Blueprint('games', __name__, template_folder='templates/games')

# Game 1 Route
@games_bp.route('/game1')
def game1():
    return "This is Game 1!"

# Game 2 Route
@games_bp.route('/game2')
def game2():
    return "This is Game 2!"

# Game 3 Route
@games_bp.route('/game3')
def game3():
    return "This is Game 3!"
