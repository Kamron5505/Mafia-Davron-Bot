from aiogram import BaseMiddleware
from aiogram.types import Message, CallbackQuery
from database.db import Database


class GroupCheckMiddleware(BaseMiddleware):
    async def __call__(self, handler, event, data):
        chat_id = None
        if isinstance(event, Message) and event.chat:
            chat_id = event.chat.id
        elif isinstance(event, CallbackQuery) and event.message and event.message.chat:
            chat_id = event.message.chat.id

        if chat_id and chat_id > 0:
            return await handler(event, data)

        if chat_id and chat_id < 0:
            db = Database()
            if await db.is_group_blocked(chat_id):
                return

        return await handler(event, data)
