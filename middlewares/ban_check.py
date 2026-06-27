from aiogram import BaseMiddleware
from aiogram.types import Message, CallbackQuery
from database.db import Database


class BanCheckMiddleware(BaseMiddleware):
    async def __call__(self, handler, event, data):
        user_id = None
        if isinstance(event, Message) and event.from_user:
            user_id = event.from_user.id
        elif isinstance(event, CallbackQuery) and event.from_user:
            user_id = event.from_user.id

        if user_id:
            db = Database()
            if await db.is_banned(user_id):
                if isinstance(event, Message):
                    await event.answer("🚫 Siz botdan bloklangansiz!")
                elif isinstance(event, CallbackQuery):
                    await event.answer("🚫 Siz botdan bloklangansiz!", show_alert=True)
                return

        return await handler(event, data)
