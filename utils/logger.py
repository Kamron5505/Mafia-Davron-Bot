from aiogram import Bot
from aiogram.exceptions import TelegramAPIError
from config import BOT_TOKEN, LOG_CHANNEL_ID
import datetime


async def send_log(action: str, details: str = "", by_user: str = ""):
    if not LOG_CHANNEL_ID or LOG_CHANNEL_ID == -100123456789:
        return
    try:
        bot = Bot(token=BOT_TOKEN)
        timestamp = datetime.datetime.now().strftime("%d.%m.%Y %H:%M:%S")
        text = (
            f"📋 *AMAL LOGI*\n"
            f"———————————————\n"
            f"🕐 Vaqt: {timestamp}\n"
            f"⚡️ Amal: {action}\n"
            f"👤 Admin: {by_user}\n"
            f"📝 Tafsilot: {details}"
        )
        await bot.send_message(LOG_CHANNEL_ID, text)
        await bot.session.close()
    except TelegramAPIError:
        pass
    except Exception:
        pass
