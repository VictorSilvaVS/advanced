import os
import sys
import logging
import logging.handlers
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from .config import Config

db = SQLAlchemy()
login_manager = LoginManager()

def create_app():
    base_path = getattr(sys, '_MEIPASS', os.path.abspath("."))
    template_path = os.path.join(base_path, "templates")
    static_path = os.path.join(base_path, "static")
    
    app = Flask(__name__, template_folder=template_path, static_folder=static_path)
    app.config.from_object(Config)

    # Configure logging
    log_formatter = logging.Formatter('%(asctime)s [%(levelname)s] [%(filename)s:%(lineno)d] %(message)s')
    log_file = 'app.log'
    file_handler = logging.handlers.RotatingFileHandler(log_file, maxBytes=5*1024*1024, backupCount=5)
    file_handler.setFormatter(log_formatter)
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(log_formatter)
    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)

    db.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'

    with app.app_context():
        from . import routes, auth, models
        app.register_blueprint(routes.bp)
        app.register_blueprint(auth.bp)
        
        # Create database tables for our models
        db.create_all()

    return app
