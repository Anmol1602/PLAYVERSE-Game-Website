from flask import render_template, request, session, redirect, url_for
import random
from utils import save_statistics
from . import games_bp

# Function to initialize stats for Rock Paper Scissors if they don't exist
def initialize_rps_stats(user_id):
    if 'user_statistics' not in session:
        session['user_statistics'] = {}
        print("Initializing user_statistics in session...")

    if 'Rock Paper Scissors' not in session['user_statistics']:
        session['user_statistics']['Rock Paper Scissors'] = {
            'games_won': 0,
            'games_lost': 0,
            'games_tied': 0,
            'games_played': 0
        }
        print("Initializing Rock Paper Scissors stats in session...")

    print(f"Current session stats: {session['user_statistics']}")

# Rock Paper Scissors Game Route
@games_bp.route("/game2", methods=["GET", "POST"])
def game2():
    choices = ["Rock", "Paper", "Scissors"]
    result = None
    user_choice = None
    computer_choice = None
    winner = None
    reset_flag = 'reset' in request.args  # Check if reset flag is passed in URL

    # Initialize stats when the game is accessed for the first time
    initialize_rps_stats(session["user_id"])

    # Handle game logic on POST request
    if request.method == "POST" and not reset_flag:
        user_choice = request.form.get("choice")
        computer_choice = random.choice(choices)

        # Determine the result of the game
        if user_choice == computer_choice:
            result = "It's a tie!"
            winner = "tie"
        elif (user_choice == "Rock" and computer_choice == "Scissors") or \
             (user_choice == "Scissors" and computer_choice == "Paper") or \
             (user_choice == "Paper" and computer_choice == "Rock"):
            result = "You win!"
            winner = "win"
        else:
            result = "You lose!"
            winner = "lose"

        # Update the statistics based on the game result
        update_rps_stats(session["user_id"], winner)

        # Save the updated statistics
        save_statistics(session["user_id"], "Rock Paper Scissors", result, session['user_statistics']['Rock Paper Scissors'])

    # Handle reset logic on GET request (when reset button is clicked)
    if reset_flag:
        # Reset only Rock Paper Scissors stats, not the entire user statistics
        if 'Rock Paper Scissors' in session['user_statistics']:
            session['user_statistics']['Rock Paper Scissors'] = {
                'games_won': 0,
                'games_lost': 0,
                'games_tied': 0,
                'games_played': 0
            }
        result = "Game reset!"  # Provide feedback
        print(f"Session stats after reset: {session['user_statistics']}")

    # Render the template with the choices, result, and stats
    return render_template("game2.html", 
                           choices=choices, 
                           result=result, 
                           user_choice=user_choice, 
                           computer_choice=computer_choice,
                           reset=reset_flag)

# Function to update stats for Rock Paper Scissors
def update_rps_stats(user_id, result):
    # Update the statistics based on the result
    if result == "win":
        session['user_statistics']['Rock Paper Scissors']['games_won'] += 1
    elif result == "tie":
        session['user_statistics']['Rock Paper Scissors']['games_tied'] += 1
    else:  # result is "lose"
        session['user_statistics']['Rock Paper Scissors']['games_lost'] += 1
    session['user_statistics']['Rock Paper Scissors']['games_played'] += 1
    
    # Log the updated session stats
    print("Session Stats game2.py: ", session['user_statistics']['Rock Paper Scissors'])
