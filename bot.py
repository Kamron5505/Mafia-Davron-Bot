import asyncio
import logging
import sys

if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import BotCommand, BotCommandScopeDefault

from config import BOT_TOKEN
from database.db import Database
from handlers import start, game, night, day, payment, broadcast
from handlers.admin import panel as admin_panel
from handlers.admin import users as admin_users
from handlers.admin import groups as admin_groups
from handlers.admin import stars as admin_stars
from handlers.admin import stats as admin_stats
from middlewares.ban_check import BanCheckMiddleware
from middlewares.group_check import GroupCheckMiddleware

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    stream=sys.stdout,
)

logger = logging.getLogger(__name__)


async def set_bot_commands(bot: Bot):
    commands = [
        BotCommand(command="start", description="Bosh menyu"),
        BotCommand(command="profile", description="Profilim"),
        BotCommand(command="help", description="Yordam"),
        BotCommand(command="language", description="Til tanlash"),
        BotCommand(command="leave", description="O'yindan chiqish"),
        BotCommand(command="admin", description="Admin panel"),
        BotCommand(command="stats", description="O'yin statistikasi"),
        BotCommand(command="buy", description="Yulduzlar sotib olish"),
    ]
    await bot.set_my_commands(commands, scope=BotCommandScopeDefault())


async def on_startup(bot: Bot):
    logger.info("Bot ishga tushmoqda...")
    db = Database()
    await db.connect()

    await set_bot_commands(bot)

    active_games = await db.get_active_games_for_recovery()
    for g in active_games:
        logger.info(f"Qayta tiklash: o'yin #{g['game_id']} ({g['status']})")
        await db.end_game(g["game_id"])

    logger.info("Bot ishga tushdi!")


async def main():
    bot = Bot(
        token=BOT_TOKEN,
        default=DefaultBotProperties(parse_mode=ParseMode.MARKDOWN),
    )

    dp = Dispatcher(storage=MemoryStorage())

    dp.message.middleware(BanCheckMiddleware())
    dp.callback_query.middleware(BanCheckMiddleware())
    dp.message.middleware(GroupCheckMiddleware())
    dp.callback_query.middleware(GroupCheckMiddleware())

    dp.include_routers(
        start.router,
        game.router,
        night.router,
        day.router,
        admin_panel.router,
        admin_users.router,
        admin_groups.router,
        admin_stars.router,
        admin_stats.router,
        payment.router,
        broadcast.router,
    )

    dp.startup.register(on_startup)

    logger.info("Bot ishlayapti...")
    await dp.start_polling(bot)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Bot to'xtatildi.")
    except Exception as e:
        logger.error(f"Xatolik: {e}")
        sys.exit(1)
