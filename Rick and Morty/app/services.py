import requests
import random
from flask import current_app

def get_all_characters():
    """Fetches all characters from the Rick and Morty API."""
    try:
        response = requests.get(f"{current_app.config['API_BASE_URL']}/character")
        response.raise_for_status()
        return response.json().get("results", []), None
    except requests.exceptions.RequestException as e:
        current_app.logger.error(f"Error fetching characters: {e}")
        return [], "Could not fetch characters from the API."

def get_all_episodes():
    """Fetches all episodes from the Rick and Morty API."""
    try:
        response = requests.get(f"{current_app.config['API_BASE_URL']}/episode")
        response.raise_for_status()
        return response.json().get("results", []), None
    except requests.exceptions.RequestException as e:
        current_app.logger.error(f"Error fetching episodes: {e}")
        return [], "Could not fetch episodes from the API."

def get_random_characters_for_quiz(count=3):
    """Fetches a specified number of random characters for the quiz."""
    try:
        # First, get the total number of characters
        char_info_response = requests.get(f"{current_app.config['API_BASE_URL']}/character")
        char_info_response.raise_for_status()
        char_info = char_info_response.json()
        character_count = char_info['info']['count']

        # Pick random character IDs
        random_ids = random.sample(range(1, character_count + 1), count)
        random_ids_str = ",".join(map(str, random_ids))

        # Fetch the random characters
        response = requests.get(f"{current_app.config['API_BASE_URL']}/character/{random_ids_str}")
        response.raise_for_status()
        return response.json(), None
    except requests.exceptions.RequestException as e:
        current_app.logger.error(f"Error fetching characters for quiz: {e}")
        return [], "Could not fetch characters for the quiz."
