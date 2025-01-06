from flask import Blueprint

# Create a blueprint for games
games_bp = Blueprint('games', __name__, template_folder='../templates')

# Import individual game routes
from . import game1, game2, game3
