from flask import render_template, request, session, redirect, url_for, flash
from . import games_bp
import random
from utils import save_statistics

@games_bp.route('/game1', methods=['GET', 'POST'])
def game1():
    game_feedback = ""  # Variable to store feedback for the game

    # Initialize game data if it's a new session or reset
    if 'target' not in session:
        session['target'] = random.randint(1, 10)
        session['attempts'] = 0
        session['game_over'] = False  # Flag to indicate the game is over

    # Ensure user_statistics is initialized in the session
    if 'user_statistics' not in session:
        session['user_statistics'] = {}

    # Ensure 'Guess the Number' statistics are initialized
    if 'Guess the Number' not in session['user_statistics']:
        session['user_statistics']['Guess the Number'] = {
            'total_attempts': 0,
            'lowest_attempts': float('inf'),
            'highest_attempts': 0,
            'games_played': 0
        }

    # Handle game logic for guessing
    if request.method == 'POST':
        if session['game_over']:  # If the game is already over, don't process guesses
            return redirect(url_for('games.game1'))  # Redirect to avoid form resubmission

        try:
            guess = int(request.form['guess'])
        except ValueError:
            game_feedback = 'Please enter a valid number between 1 and 10.'
            return render_template('game1.html', 
                                   attempts=session['attempts'], 
                                   feedback=game_feedback)

        session['attempts'] += 1
        max_attempts = 5

        if guess == session['target']:
            attempts = session['attempts']
            game_feedback = f'Congratulations! You guessed it in {attempts} attempts.'

            # Save statistics to the score.json
            save_statistics(session['user_id'], 'Guess the Number', 'win', {
                'total_attempts': session['attempts'],
                'lowest_attempts': min(session['user_statistics']['Guess the Number']['lowest_attempts'], attempts),
                'highest_attempts': max(session['user_statistics']['Guess the Number']['highest_attempts'], attempts)
            })
            session['user_statistics']['Guess the Number']['games_played'] += 1
            print("Session Stats game1.py: ", session['user_statistics']['Guess the Number'])
            # Mark the game as over
            session['game_over'] = True

        elif session['attempts'] >= max_attempts:
            correct_number = session['target']
            game_feedback = f'Sorry! You have reached the maximum attempts. The correct number was {correct_number}.'

            # Save statistics to the score.json
            save_statistics(session['user_id'], 'Guess the Number', 'lose', {
                'total_attempts': session['attempts']
            })
            session['user_statistics']['Guess the Number']['games_played'] += 1
            print("Session Stats game1.py: ", session['user_statistics']['Guess the Number'])
            # Mark the game as over
            session['game_over'] = True

        elif guess < session['target']:
            game_feedback = 'Too low! Try again.'
        else:
            game_feedback = 'Too high! Try again.'

    # Handle reset logic on GET request (when reset button is clicked)
    if request.method == 'GET' and 'reset' in request.args:
        # Reset only the necessary game data
        session.pop('target', None)
        session.pop('attempts', None)
        session['game_over'] = False  # Reset the game over flag
        game_feedback = 'Game reset!'
        # Re-initialize the session for a new game
        session['target'] = random.randint(1, 10)
        session['attempts'] = 0
        print("Session Reset game1.py: ", session['user_statistics']['Guess the Number'])

    return render_template('game1.html', 
                           attempts=session.get('attempts', 0), 
                           feedback=game_feedback)
