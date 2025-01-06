from flask import render_template, request, session, flash
from . import games_bp
import random
from utils import save_statistics

@games_bp.route("/game3", methods=["GET", "POST"])
def game3():
    if "question" not in session:
        # Generate a more complex equation
        num1 = random.randint(1, 20)
        num2 = random.randint(1, 20)
        num3 = random.randint(1, 20)
        operator1 = random.choice(["+", "-", "*", "/"])
        operator2 = random.choice(["+", "-", "*", "/"])
        
        # Ensure division is by non-zero and results in an integer
        if operator1 == "/":
            num2 = random.randint(1, 20)
            num1 = num2 * random.randint(1, 10)  # Ensure num1 is divisible by num2
        if operator2 == "/":
            num3 = random.randint(1, 20)
            temp_result = eval(f"{num1} {operator1} {num2}")
            num3 = num3 if temp_result % num3 == 0 else 1  # Ensure result is divisible

        question = f"({num1} {operator1} {num2}) {operator2} {num3}"
        answer = eval(question)
        
        session["question"] = question
        session["answer"] = answer

    if request.method == "POST":
        try:
            user_answer = float(request.form["answer"])
            if user_answer == session["answer"]:
                flash("Correct! Great job!", "success")
                save_statistics(session.get('user_id'), 'Math Quiz', "win")  # Record a win
                session.pop("question", None)
                session.pop("answer", None)
            else:
                flash("Wrong answer. Try again.", "danger")
                save_statistics(session.get('user_id'), 'Math Quiz', "lose")  # Record a loss
        except ValueError:
            flash("Please enter a valid number.", "warning")

    return render_template("game3.html", question=session.get("question"))
