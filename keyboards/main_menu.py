from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder


def main_menu_kb() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(text="🎮 Chatga o'yin qo'shish", callback_data="add_game"),
    )
    builder.row(
        InlineKeyboardButton(text="🎲 Chatga kirish", callback_data="join_chat"),
    )
    builder.row(
        InlineKeyboardButton(text="🌐 Til / Language", callback_data="language"),
    )
    builder.row(
        InlineKeyboardButton(text="👤 Profil | 🎭 Rollar", callback_data="profile_roles"),
    )
    return builder.as_markup()


def profile_roles_kb() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(text="👤 Profil", callback_data="profile"),
        InlineKeyboardButton(text="🎭 Rollar", callback_data="roles_list"),
    )
    builder.row(
        InlineKeyboardButton(text="🔙 Orqaga", callback_data="back_main"),
    )
    return builder.as_markup()


def back_kb() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(text="🔙 Orqaga", callback_data="back_main"),
    )
    return builder.as_markup()


def confirm_leave_kb() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(text="✅ Ha, chiqish", callback_data="confirm_leave"),
        InlineKeyboardButton(text="❌ Yo'q", callback_data="cancel_leave"),
    )
    return builder.as_markup()
