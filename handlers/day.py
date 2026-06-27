from aiogram import Router, F
from aiogram.types import CallbackQuery, Message
from aiogram.filters import Command
from database.db import Database
from keyboards.game_kb import end_game_kb
from utils.messages import *
from utils.game_logic import check_win_condition
from utils.state import active_games
from config import MIN_PLAYERS

router = Router()
db = Database()


@router.callback_query(F.data.startswith("vote:"))
async def handle_vote(callback: CallbackQuery):
    data = callback.data.split(":")
    game_id = int(data[1])
    target_id = data[2]

    game = active_games.get(game_id)
    if not game or game["phase"] != "voting":
        await callback.answer("❌ Ovoz berish vaqti o'tdi!", show_alert=True)
        return

    user_id = callback.from_user.id
    if user_id not in game["players"] or not game["players"][user_id]["alive"]:
        await callback.answer(NOT_ALIVE, show_alert=True)
        return

    if game["players"][user_id]["voted"]:
        await callback.answer(ALREADY_VOTED, show_alert=True)
        return

    if target_id == "skip":
        game["players"][user_id]["voted"] = True
        game["players"][user_id]["vote_target"] = None
        await db.set_vote(game_id, user_id, 0)
        await callback.answer("⏭ Ovoz bermadingiz")
        return

    if target_id == "results":
        alive = {uid: pd for uid, pd in game["players"].items() if pd["alive"]}
        vote_text = "📊 *Ovozlar holati:*\n"
        for uid, pd in alive.items():
            status = "✅ Ovoz berdi" if pd["voted"] else "⏳ Hali bermadi"
            name = pd.get("name", f"ID{uid}")
            vote_text += f"• {name}: {status}\n"
        await callback.answer(vote_text, show_alert=True)
        return

    target_id = int(target_id)
    if target_id not in game["players"] or not game["players"][target_id]["alive"]:
        await callback.answer("❌ Bu o'yinchi o'lik yoki mavjud emas!", show_alert=True)
        return

    game["players"][user_id]["voted"] = True
    game["players"][user_id]["vote_target"] = target_id
    await db.set_vote(game_id, user_id, target_id)

    await callback.answer(VOTE_CONFIRMED, show_alert=True)

    all_voted = all(
        pd["voted"] for uid, pd in game["players"].items() if pd["alive"]
    )
    if all_voted:
        from handlers.game import resolve_votes
        await resolve_votes(game_id, game["chat_id"])


@router.message(Command("forcestart"))
async def cmd_forcestart(message: Message):
    chat = message.chat
    if chat.type == "private":
        await message.answer("❌ Bu buyruq faqat guruhda ishlaydi.")
        return

    member = await chat.get_member(message.from_user.id)
    if member.status not in ("creator", "administrator"):
        await message.answer(ADMIN_ONLY)
        return

    game = None
    game_id = None
    for gid, g in active_games.items():
        if g.get("chat_id") == chat.id and g["phase"] == "lobby":
            game = g
            game_id = gid
            break

    if not game:
        await message.answer(GAME_NOT_FOUND)
        return

    if len(game["players"]) < MIN_PLAYERS:
        await message.answer(NOT_ENOUGH_PLAYERS.format(count=len(game["players"])))
        return

    await message.answer(FORCE_START)
    from handlers.game import start_game as sg
    await sg(game_id, chat.id)


@router.message(Command("stats"))
async def cmd_stats(message: Message):
    chat = message.chat
    if chat.type == "private":
        await message.answer("❌ Bu buyruq faqat guruhda ishlaydi.")
        return

    game = None
    game_id = None
    for gid, g in active_games.items():
        if g.get("chat_id") == chat.id and g["phase"] != "ended":
            game = g
            game_id = gid
            break

    if not game:
        await message.answer(GAME_NOT_FOUND)
        return

    alive = []
    dead = []
    for uid, pd in game["players"].items():
        name = pd.get("name", f"ID{uid}")
        entry = f"{pd['role'].short_name()} — {name}"
        if pd["alive"]:
            alive.append(entry)
        else:
            dead.append(entry)

    events = await db.get_events(game_id)
    event_text = "\n".join(f"• {e['description']}" for e in events[-5:]) or "Hodisalar yo'q"

    text = GAME_STATS.format(
        roles=", ".join(pd['role'].short_name() for pd in game["players"].values()),
        events=event_text,
        alive=len(alive),
        alive_list="\n".join(alive) if alive else "—",
        dead_list="\n".join(dead) if dead else "—",
    )
    await message.answer(text)
