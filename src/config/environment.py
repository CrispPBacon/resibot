from dotenv import load_dotenv
import os

load_dotenv()
ENV = os.getenv("FLASK_ENV", "development")
SECRET_KEY = os.getenv("SECRET_KEY", "default-secret")
PORT = int(os.getenv("PORT", 3000))
FRONTEND_URL = os.getenv("FRONTEND_URL", "http://127.0.0.1:3000")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "ENTER_OPENAI_API_KEY")
TELEGRAM_BOT_TOKEN = os.getenv(
    "TELEGRAM_BOT_TOKEN", "ENTER_TELEGRAM_BOT_TOKEN")
