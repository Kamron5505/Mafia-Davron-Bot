import os
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = "8954728309:AAHhv2kHbP46KYOVnwtPcfHFuWim0Kb0ZIM"
DB_PATH = "mafia_bot.db"

OWNER_ID = 7067830755
LOG_CHANNEL_ID = -100123456789

GAME_JOIN_TIME = 60
DAY_DISCUSSION_TIME = 300
VOTE_TIME = 60
NIGHT_ACTION_TIME = 30

MIN_PLAYERS = 6
MAX_PLAYERS = 30

ROLES_PER_GAME = 6

ADMIN_IDS = []

STARS_PACKAGES = [
    {"name": "Starter", "stars": 50, "price": 50},
    {"name": "Pro", "stars": 150, "price": 130},
    {"name": "Elite", "stars": 300, "price": 250},
    {"name": "Legend", "stars": 700, "price": 500},
]
