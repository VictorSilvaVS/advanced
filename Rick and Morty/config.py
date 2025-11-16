import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'you-will-never-guess'
    API_BASE_URL = "https://rickandmortyapi.com/api"
