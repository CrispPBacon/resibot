from flask import Flask
from .config import load_config, on_telegram_init
from .telegram_route import telegram_bp


def create_app():
    app = Flask(__name__)

    # Load configs
    load_config(app)
    on_telegram_init()
    # Blueprints
    app.register_blueprint(telegram_bp, url_prefix="/api/telegram")
    return app
