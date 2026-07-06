import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID", "")
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY", "")
PRODUCT_HUNT_TOKEN = os.getenv("PRODUCT_HUNT_TOKEN", "")
CRUNCHBASE_API_KEY = os.getenv("CRUNCHBASE_API_KEY", "")

DATABASE_PATH = os.getenv("DATABASE_PATH", str(BASE_DIR / "data" / "niche.db"))
CORS_ORIGINS = [o.strip() for o in os.getenv("CORS_ORIGINS", "http://localhost:5173").split(",")]

CLAUDE_MODEL = os.getenv("CLAUDE_MODEL", "claude-sonnet-5")
