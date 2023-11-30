from flask import Flask
from config import Config  # Import the Config class from config.py
from app.routes import main_blueprint

app = Flask(__name__)

# Register the blueprint
app.register_blueprint(main_blueprint)

app.config.from_object(Config)  # Load configuration variables from Config class
