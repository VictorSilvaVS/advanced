import os
from datetime import timedelta

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'a7da6230bce08f317c2a0de0d383740c7f21b168a7da6230bce08f317c2a0de0d383740c7f21b168'
    PERMANENT_SESSION_LIFETIME = timedelta(minutes=15)
    SESSION_PERMANENT = True
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///hotspots.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    UPLOAD_FOLDER = 'static/uploads'
    ALLOWED_EXTENSIONS = {'jpg', 'jpeg', 'png', 'gif', 'pdf', 'mp4', 'avi', 'mov', 'mkv', 'jfif'}
