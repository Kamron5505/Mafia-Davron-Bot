import os
from dotenv import load_dotenv

load_dotenv()

# Telegram Bot
BOT_TOKEN = os.getenv("BOT_TOKEN", "")

# Database
DB_PATH = os.getenv("DB_PATH", "mafia_bot.db")

# Owner & Admins
OWNER_ID = int(os.getenv("OWNER_ID", "0"))
LOG_CHANNEL_ID = int(os.getenv("LOG_CHANNEL_ID", "0"))
ADMIN_IDS_STR = os.getenv("ADMIN_IDS", "")
ADMIN_IDS = [int(x.strip()) for x in ADMIN_IDS_STR.split(",") if x.strip()]

# Game timings (seconds)
GAME_JOIN_TIME = int(os.getenv("GAME_JOIN_TIME", "60"))
DAY_DISCUSSION_TIME = int(os.getenv("DAY_DISCUSSION_TIME", "300"))
VOTE_TIME = int(os.getenv("VOTE_TIME", "60"))
NIGHT_ACTION_TIME = int(os.getenv("NIGHT_ACTION_TIME", "30"))

# Game limits
MIN_PLAYERS = int(os.getenv("MIN_PLAYERS", "6"))
MAX_PLAYERS = int(os.getenv("MAX_PLAYERS", "30"))
ROLES_PER_GAME = int(os.getenv("ROLES_PER_GAME", "6"))

# Stars packages
STARS_PACKAGES = [
    {"name": "Starter", "stars": 50, "price": 50},
    {"name": "Pro", "stars": 150, "price": 130},
    {"name": "Elite", "stars": 300, "price": 250},
    {"name": "Legend", "stars": 700, "price": 500},
]
