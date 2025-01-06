from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_mail import Mail, Message
from itsdangerous import (
    URLSafeTimedSerializer as Serializer,
    BadSignature,
    SignatureExpired,
)
import bcrypt
import os
from utils import read_json, write_json
from flask import Blueprint
from games import game1, game2, game3  # Make sure games.py is correctly imported
from games import games_bp  # Ensure this is imported

# Create a Flask instance
app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "fallback_dev_key")

# Email Configuration
app.config["MAIL_SERVER"] = "smtp.gmail.com"
app.config["MAIL_PORT"] = 465
app.config["MAIL_USERNAME"] = "anmol16072002@gmail.com"
app.config["MAIL_PASSWORD"] = os.getenv(
    "MAIL_PASSWORD"
)  # Get password from environment variable
app.config["MAIL_USE_TLS"] = False
app.config["MAIL_USE_SSL"] = True
app.config["MAIL_DEFAULT_SENDER"] = "anmol16072002@gmail.com"

mail = Mail(app)


# Home Route
@app.route("/")
def home():
    return render_template("home.html")


# Sign In Route
@app.route("/signin", methods=["GET", "POST"])
def signin():
    if request.method == "POST":
        username = request.form["username"]
        email = request.form["email"]
        password = request.form["password"]

        # Hash the password before storing it
        hashed_password = bcrypt.hashpw(
            password.encode("utf-8"), bcrypt.gensalt()
        ).decode("utf-8")

        users = read_json("users.json")

        # Check if the email already exists
        if any(u["email"] == email for u in users):
            flash("Email already exists!", "danger")
            return redirect(url_for("signin"))

        new_user = {
            "id": len(users) + 1,
            "username": username,
            "email": email,
            "password": hashed_password,
        }
        users.append(new_user)
        write_json("users.json", users)

        # Set session after user is created
        session["user_id"] = new_user["id"]
        session["username"] = new_user["username"]

        flash("User created successfully! Please log in.", "success")
        return redirect(url_for("login"))  # Redirect to login page

    return render_template("signin.html")


# Login Route
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]

        users = read_json("users.json")
        user = next((u for u in users if u["email"] == email), None)

        if user and bcrypt.checkpw(
            password.encode("utf-8"), user["password"].encode("utf-8")
        ):
            session["user_id"] = user["id"]
            session["username"] = user["username"]
            flash("Login successful!", "success")
            return redirect(url_for("dashboard"))
        else:
            flash("Invalid email or password!", "danger")

    return render_template("login.html")


# Logout Route
@app.route('/logout')
def logout():
    session.clear()  # This will clear all session data, including attempts and game stats
    flash("You have logged out.", 'info')
    return redirect(url_for('home'))  # Redirect to home or login page


# Dashboard Route
@app.route("/dashboard")
def dashboard():
    # Check if the user is logged in
    if "user_id" not in session:
        return redirect(url_for("auth.login"))

    # List of available games
    games = [
        {
            "name": "Guess the Number",
            "description": "Guess the number",
            "url": url_for("games.game1"),
        },
        {
            "name": "Rock Paper Scissors",
            "description": "Rock Paper Scissors",
            "url": url_for("games.game2"),
        },
        {
            "name": "Maths Quiz",
            "description": "Maths Quiz",
            "url": url_for("games.game3"),
        },
    ]

    # Fetch scores for the logged-in user
    scores = read_json("score.json")
    user_scores = [s for s in scores if s["user_id"] == session["user_id"]]

    # Render the dashboard template with the user's game statistics
    return render_template(
        "dashboard.html",
        games=games,
        statistics=user_scores,  # Corrected to pass the user scores as statistics
        username=session.get("username"),
    )


# Password Reset Request Route
@app.route("/reset_password", methods=["GET", "POST"])
def reset_password():
    if request.method == "POST":
        email = request.form["email"]
        users = read_json("users.json")

        user = next((u for u in users if u["email"] == email), None)
        if user:
            # Generate the token
            serializer = Serializer(app.secret_key)
            token = serializer.dumps(email, salt="password-reset")

            # Send email with the reset link
            reset_url = url_for("reset_password_form", token=token, _external=True)
            msg = Message("Password Reset Request", recipients=[email])
            msg.body = f"Click the link to reset your password: {reset_url}"
            mail.send(msg)

            flash("Password reset link sent to your email!", "success")
            return redirect(url_for("login"))
        else:
            flash("Email not found!", "danger")

    return render_template("reset_password.html")


# Password Reset Form Route
@app.route("/reset_password/<token>", methods=["GET", "POST"])
def reset_password_form(token):
    try:
        serializer = Serializer(app.secret_key)
        email = serializer.loads(
            token, salt="password-reset", max_age=3600
        )  # 1 hour expiry
    except (BadSignature, SignatureExpired):
        flash("The reset link is invalid or expired!", "danger")
        return redirect(url_for("login"))

    if request.method == "POST":
        new_password = request.form["password"]
        users = read_json("users.json")

        user = next((u for u in users if u["email"] == email), None)
        if user:
            # Hash the new password
            hashed_password = bcrypt.hashpw(
                new_password.encode("utf-8"), bcrypt.gensalt()
            ).decode("utf-8")
            user["password"] = hashed_password
            write_json("users.json", users)
            flash("Password reset successfully!", "success")
            return redirect(url_for("login"))
        else:
            flash("User not found!", "danger")

    return render_template("reset_password_form.html")


# Profile Editing Route
@app.route("/edit_profile", methods=["GET", "POST"])
def edit_profile():
    if "user_id" not in session:
        return redirect(url_for("login"))

    users = read_json("users.json")
    user = next((u for u in users if u["id"] == session["user_id"]), None)

    if request.method == "POST":
        new_username = request.form["username"]
        new_email = request.form["email"]
        new_address = request.form["address"]
        new_phone = request.form["phone"]

        if new_username:
            user["username"] = new_username
            session["username"] = new_username  # Update session with the new username
        if new_email:
            user["email"] = new_email
        if new_address:
            user["address"] = new_address
        if new_phone:
            user["phone"] = new_phone

        write_json("users.json", users)
        flash("Profile updated successfully!", "success")
        return redirect(url_for("dashboard"))

    return render_template("edit_profile.html", user=user)


@app.route("/about")
def about():
    return render_template("about.html")


@app.route("/contact", methods=["GET", "POST"])
def contact():
    if request.method == "POST":
        name = request.form["name"]
        email = request.form["email"]
        subject = request.form["subject"]
        message = request.form["message"]

        # Save message to the JSON database
        messages = read_json("contact_messages.json")
        new_message = {
            "id": len(messages) + 1,
            "name": name,
            "email": email,
            "subject": subject,
            "message": message,
        }
        messages.append(new_message)
        write_json("contact_messages.json", messages)

        # Send email notification
        try:
            msg = Message(
                subject=f"Thank You for Your Query: {subject}",
                sender=app.config["MAIL_DEFAULT_SENDER"],
                recipients=[email],  # Replace with your email
                body=f"""
Dear {name},

Thank you for reaching out to us. We have received your query with the following details:

Query Category: {subject}
Query : {message}

Our team will review your message and respond to you at the earliest opportunity. If you have any further questions or need immediate assistance, please do not hesitate to contact us.

Best regards,
[Your Company Name or Support Team]

This is an automated confirmation email. Please do not reply to this message.
                """,
            )
            mail.send(msg)
            flash(
                "Your message has been sent successfully. We will get back to you soon.",
                "success",
            )
        except Exception as e:
            flash(f"An error occurred while sending the email: {str(e)}", "danger")

        return redirect(url_for("contact"))

    return render_template("contact.html")


@app.route("/team")
def team():
    return render_template("team.html")


# Game routes
app.register_blueprint(games_bp, url_prefix="/games")

# Run the app
if __name__ == "__main__":
    app.run(debug=True)
