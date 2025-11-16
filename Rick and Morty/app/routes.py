from flask import render_template, request, redirect, url_for, Blueprint
from app import services

bp = Blueprint('main', __name__)

@bp.route("/")
def index():
    """Renders the home page."""
    return render_template("index.html")

@bp.route("/login", methods=["GET", "POST"])
def login():
    """Renders the login page and handles login attempts."""
    if request.method == "POST":
        return redirect(url_for("main.index"))
    return render_template("login.html")

@bp.route("/personagens")
def characters():
    """Fetches and displays the list of characters."""
    character_list, error = services.get_all_characters()
    return render_template("characters.html", characters=character_list, error=error)

@bp.route("/episodios")
def episodes():
    """Fetches and displays the list of episodes."""
    episode_list, error = services.get_all_episodes()
    return render_template("episodes.html", episodes=episode_list, error=error)

@bp.route("/quiz")
def quiz():
    """Fetches random characters for the quiz."""
    character_list, error = services.get_random_characters_for_quiz(count=3)
    return render_template("quiz.html", characters=character_list, error=error)
