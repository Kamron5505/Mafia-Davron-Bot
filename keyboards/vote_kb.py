from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder


def vote_kb(players: list, game_id: int) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.max_width = 2
    for p in players:
        name = p.get("username") or p.get("first_name") or f"ID{p['user_id']}"
        builder.row(
            InlineKeyboardButton(
                text=name,
                callback_data=f"vote:{game_id}:{p['user_id']}",
            )
        )
    builder.row(
        InlineKeyboardButton(
            text="❌ Hech kim",
            callback_data=f"vote:{game_id}:skip",
        ),
        InlineKeyboardButton(
            text="📊 Natijalar",
            callback_data=f"vote:{game_id}:results",
        ),
    )
    return builder.as_markup()


def vote_results_kb(vote_counts: dict, game_id: int) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    for user_id, count in sorted(vote_counts.items(), key=lambda x: x[1], reverse=True):
        name = vote_counts.get(f"name_{user_id}", f"ID{user_id}")
        builder.row(
            InlineKeyboardButton(
                text=f"{name} — {count} ovoz",
                callback_data=f"vote_detail:{game_id}:{user_id}",
            )
        )
    builder.row(
        InlineKeyboardButton(text="🔙 Orqaga", callback_data=f"vote_back:{game_id}"),
    )
    return builder.as_markup()


def skip_vote_kb(game_id: int) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(text="⏭ O'tkazib yuborish", callback_data=f"vote:{game_id}:skip"),
    )
    return builder.as_markup()
