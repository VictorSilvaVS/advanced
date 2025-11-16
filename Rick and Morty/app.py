import random
import logging
from flask import Flask, render_template, request, redirect, url_for
import requests
from config import Config

# Configure logging
logging.basicConfig(level=logging.INFO)

# The user should have renamed the 'app' folder to 'static'.
# If they reverted that, this line needs to be changed back to static_folder='app'.
app = Flask(__name__, static_folder='static')
app.config.from_object(Config)


@app.route("/")
def index():
    """Renders the home page."""
    return render_template("index.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    """Renders the login page and handles login attempts."""
    if request.method == "POST":
        # For now, just redirect to the home page
        return redirect(url_for("index"))
    return render_template("login.html")


@app.route("/personagens")
def characters():
    """Fetches and displays the list of characters."""
    try:
        response = requests.get(f"{app.config['API_BASE_URL']}/character")
        response.raise_for_status()  # Will raise an HTTPError for bad responses
        data = response.json()
        return render_template("characters.html", characters=data.get("results", []))
    except requests.exceptions.RequestException as e:
        app.logger.error(f"Error fetching characters: {e}")
        return render_template("characters.html", characters=[], error="Could not fetch characters from the API.")


@app.route("/episodios")
def episodes():
    """Fetches and displays the list of episodes."""
    try:
        response = requests.get(f"{app.config['API_BASE_URL']}/episode")
        response.raise_for_status()
        data = response.json()
        return render_template("episodes.html", episodes=data.get("results", []))
    except requests.exceptions.RequestException as e:
        app.logger.error(f"Error fetching episodes: {e}")
        return render_template("episodes.html", episodes=[], error="Could not fetch episodes from the API.")


@app.route("/quiz")
def quiz():
    """Fetches random characters for the quiz."""
    try:
        # First, get the total number of characters
        char_info_response = requests.get(f"{app.config['API_BASE_URL']}/character")
        char_info_response.raise_for_status()
        char_info = char_info_response.json()
        character_count = char_info['info']['count']

        # Pick 3 random character IDs
        random_ids = random.sample(range(1, character_count + 1), 3)
        random_ids_str = ",".join(map(str, random_ids))

        # Fetch the random characters
        response = requests.get(f"{app.config['API_BASE_URL']}/character/{random_ids_str}")
        response.raise_for_status()
        characters = response.json()
        return render_template("quiz.html", characters=characters)
    except requests.exceptions.RequestException as e:
        app.logger.error(f"Error fetching characters for quiz: {e}")
        return render_template("quiz.html", characters=[], error="Could not fetch characters for the quiz.")


if __name__ == "__main__":
    app.run(debug=True)