from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder


def join_game_kb(game_id: int) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(text="➕ Qo'shilish", callback_data=f"join_game:{game_id}"),
    )
    return builder.as_markup()


def game_action_kb(game_id: int, is_admin: bool = False) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(text="👥 O'yinga qo'shilish", callback_data=f"join_game:{game_id}"),
    )
    if is_admin:
        builder.row(
            InlineKeyboardButton(text="▶️ Majburiy start", callback_data=f"force_start:{game_id}"),
        )
    builder.row(
        InlineKeyboardButton(text="🚪 Chiqish", callback_data=f"leave_game:{game_id}"),
    )
    return builder.as_markup()


def player_list_kb(players: list, prefix: str = "target") -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    for p in players:
        name = p.get("username") or p.get("first_name") or f"ID{p['user_id']}"
        builder.row(
            InlineKeyboardButton(
                text=name,
                callback_data=f"{prefix}:{p['user_id']}",
            )
        )
    builder.row(
        InlineKeyboardButton(text="⏭ O'tkazib yuborish", callback_data=f"{prefix}:skip"),
    )
    return builder.as_markup()


def night_action_kb(players: list, action_type: str) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    for p in players:
        name = p.get("username") or p.get("first_name") or f"ID{p['user_id']}"
        builder.row(
            InlineKeyboardButton(
                text=f"🎯 {name}",
                callback_data=f"night:{action_type}:{p['user_id']}",
            )
        )
    builder.row(
        InlineKeyboardButton(text="⏭ Harakatsiz", callback_data=f"night:{action_type}:skip"),
    )
    return builder.as_markup()


def mafia_vote_kb(players: list) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    for p in players:
        name = p.get("username") or p.get("first_name") or f"ID{p['user_id']}"
        builder.row(
            InlineKeyboardButton(
                text=f"☠️ {name}",
                callback_data=f"mafia_kill:{p['user_id']}",
            )
        )
    builder.row(
        InlineKeyboardButton(text="⏭ Hech kim", callback_data="mafia_kill:skip"),
    )
    return builder.as_markup()


def end_game_kb() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(text="🏠 Bosh menyu", callback_data="back_main"),
        InlineKeyboardButton(text="🎮 Qayta o'ynash", callback_data="rematch"),
    )
    return builder.as_markup()
