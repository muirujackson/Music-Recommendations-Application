from flask import Flask
from config import Config  # Import the Config class from config.py
from app.routes import main_blueprint

app = Flask(__name__)

# Register the blueprint
app.register_blueprint(main_blueprint)

app.config.from_object(Config)
app.secret_key = 'ownerproof-3527117-1701511015-e9c562a416e9'
