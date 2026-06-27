import asyncio
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, ChatMemberUpdated
from aiogram.filters import Command, ChatMemberUpdatedFilter
from aiogram.exceptions import TelegramBadRequest
from database.db import Database
from keyboards.game_kb import join_game_kb, game_action_kb, player_list_kb, end_game_kb
from keyboards.vote_kb import vote_kb
from utils.messages import *
from utils.role_selector import select_roles, assign_roles
from utils.game_logic import check_win_condition, resolve_night_actions, generate_death_story
from roles.base_role import get_role
from config import GAME_JOIN_TIME, VOTE_TIME, MIN_PLAYERS, MAX_PLAYERS, ROLES_PER_GAME
from utils.state import active_games, game_timers

router = Router()
db = Database()


@router.message(Command("startgame"))
async def start_game_lobby(message: Message):
    chat = message.chat
    if chat.type == "private":
        await message.answer("❌ O'yinni faqat guruh chatlarida boshlash mumkin!")
        return

    member = await chat.get_member(message.from_user.id)
    if member.status not in ("creator", "administrator"):
        await message.answer(ADMIN_ONLY)
        return

    existing = await db.get_active_game(chat.id)
    if existing:
        await message.answer(GAME_ALREADY_STARTED)
        return

    game_id = await db.create_game(chat.id)
    await db.record_event(game_id, "game_start", f"O'yin boshlandi. Admin: {message.from_user.first_name}")

    active_games[game_id] = {
        "players": {},
        "phase": "lobby",
        "night": 0,
        "chat_id": chat.id,
        "started_by": message.from_user.id,
    }

    await message.answer(
        LOBBY_STARTED.format(
            count=0, max=MAX_PLAYERS,
            players="Hali hech kim qo'shilmadi",
            time=GAME_JOIN_TIME,
        ),
        reply_markup=join_game_kb(game_id),
    )

    game_timers[game_id] = asyncio.create_task(lobby_timer(game_id, chat.id))


async def lobby_timer(game_id: int, chat_id: int):
    await asyncio.sleep(GAME_JOIN_TIME)
    game = active_games.get(game_id)
    if not game or game["phase"] != "lobby":
        return

    if len(game["players"]) < MIN_PLAYERS:
        try:
            from aiogram import Bot
            from config import BOT_TOKEN
            bot = Bot(token=BOT_TOKEN)
            await bot.send_message(chat_id, NOT_ENOUGH_PLAYERS.format(count=len(game["players"])))
            await bot.session.close()
        except Exception:
            pass
        await db.update_game_status(game_id, "ended", "ended")
        active_games.pop(game_id, None)
        return

    await start_game(game_id, chat_id)


async def start_game(game_id: int, chat_id: int):
    from aiogram import Bot
    from config import BOT_TOKEN
    bot = Bot(token=BOT_TOKEN)

    game = active_games.get(game_id)
    if not game:
        await bot.session.close()
        return

    player_ids = list(game["players"].keys())
    selected_roles = select_roles(ROLES_PER_GAME)
    assignments = assign_roles(player_ids, selected_roles)

    await bot.send_message(chat_id, GAME_STARTING)

    for user_id, role in assignments.items():
        await db.add_player_to_game(
            game_id, user_id, role.name, role.title, role.team,
        )
        game["players"][user_id] = {
            "role": role,
            "alive": True,
            "voted": False,
            "vote_target": None,
        }
        try:
            role_text = ROLE_DISTRIBUTION.format(
                role=role.full_name(),
                description=role.description,
                team_label=role.team_label(),
            )
            await bot.send_message(user_id, role_text)
        except Exception:
            pass

    await db.update_game_status(game_id, "night", "night")
    game["phase"] = "night"
    game["night"] = 1

    await bot.send_message(chat_id, NIGHT_START.format(night=1))

    mafia_players = [
        p for p in game["players"].items()
        if p[1]["role"].team == "mafia" and p[1]["alive"]
    ]

    for user_id, pdata in game["players"].items():
        if not pdata["alive"]:
            continue
        role = pdata["role"]
        if role.night_action or role.passive:
            try:
                if role.team == "mafia" and role.action_type == "kill":
                    alive_others = [
                        {"user_id": uid, "username": game["players"][uid].get("name", f"ID{uid}")}
                        for uid, pd in game["players"].items()
                        if pd["alive"] and pd["role"].team != "mafia"
                    ]
                    if alive_others:
                        await bot.send_message(
                            user_id,
                            f"{role.full_name()}\n\nKimni o'ldiramiz?",
                            reply_markup=player_list_kb(alive_others, f"mafia_kill:{game_id}"),
                        )
                    else:
                        await bot.send_message(user_id, NIGHT_WAIT)
                elif role.action_type == "heal":
                    alive_players = [
                        {"user_id": uid, "username": game["players"][uid].get("name", f"ID{uid}")}
                        for uid, pd in game["players"].items()
                        if pd["alive"]
                    ]
                    await bot.send_message(
                        user_id,
                        NIGHT_ACTION_PROMPT.format(role=role.full_name(), description=role.description),
                        reply_markup=player_list_kb(alive_players, f"heal:{game_id}"),
                    )
                elif role.action_type == "investigate":
                    others = [
                        {"user_id": uid, "username": game["players"][uid].get("name", f"ID{uid}")}
                        for uid, pd in game["players"].items()
                        if pd["alive"] and uid != user_id
                    ]
                    await bot.send_message(
                        user_id,
                        NIGHT_ACTION_PROMPT.format(role=role.full_name(), description=role.description),
                        reply_markup=player_list_kb(others, f"investigate:{game_id}"),
                    )
                else:
                    await bot.send_message(user_id, NIGHT_WAIT)
            except Exception:
                pass
        else:
            try:
                await bot.send_message(user_id, NIGHT_WAIT)
            except Exception:
                pass

    game["phase"] = "night_action"
    game_timers[game_id] = asyncio.create_task(night_timer(game_id, chat_id))
    await bot.session.close()


async def night_timer(game_id: int, chat_id: int):
    from aiogram import Bot
    from config import BOT_TOKEN
    bot = Bot(token=BOT_TOKEN)

    await asyncio.sleep(30)
    game = active_games.get(game_id)
    if not game or game["phase"] != "night_action":
        await bot.session.close()
        return

    await resolve_night_and_start_day(game_id, chat_id, bot)
    await bot.session.close()


async def resolve_night_and_start_day(game_id: int, chat_id: int, bot=None):
    from aiogram import Bot
    from config import BOT_TOKEN
    if bot is None:
        bot = Bot(token=BOT_TOKEN)

    game = active_games.get(game_id)
    if not game:
        await bot.session.close()
        return

    actions = []
    for user_id, pdata in game["players"].items():
        if pdata.get("night_action"):
            actions.append({
                "user_id": user_id,
                "action_type": pdata["night_action"]["type"],
                "target_id": pdata["night_action"]["target"],
            })

    deaths = resolve_night_actions(actions, game["players"])

    death_text = ""
    if deaths:
        for dead_id in deaths:
            if dead_id in game["players"]:
                game["players"][dead_id]["alive"] = False
                await db.kill_player(game_id, dead_id)
                role = game["players"][dead_id]["role"]
                death_text += DEATH_ANNOUNCEMENT.format(
                    player=game["players"][dead_id].get("name", f"ID{dead_id}"),
                    role=role.full_name(),
                    reason=generate_death_story(role.name),
                ) + "\n\n"
    else:
        death_text = NO_DEATHS

    winner = check_win_condition([
        {"user_id": uid, "team": pd["role"].team, "alive": pd["alive"]}
        for uid, pd in game["players"].items()
    ])

    if winner:
        await end_game(game_id, chat_id, winner)
        await bot.session.close()
        return

    await db.update_game_status(game_id, "day", "day")
    game["phase"] = "day"

    msg = DAY_START.format(night=game["night"], deaths=death_text)
    await bot.send_message(chat_id, msg)

    game_timers[game_id] = asyncio.create_task(day_discussion_timer(game_id, chat_id, bot))


async def day_discussion_timer(game_id: int, chat_id: int, bot):
    from config import DAY_DISCUSSION_TIME
    await asyncio.sleep(DAY_DISCUSSION_TIME)

    game = active_games.get(game_id)
    if not game or game["phase"] != "day":
        return

    await start_voting(game_id, chat_id, bot)


async def start_voting(game_id: int, chat_id: int, bot=None):
    from aiogram import Bot
    from config import BOT_TOKEN
    if bot is None:
        bot = Bot(token=BOT_TOKEN)

    game = active_games.get(game_id)
    if not game:
        await bot.session.close()
        return

    alive_players = [
        {"user_id": uid, "username": pd.get("name", f"ID{uid}")}
        for uid, pd in game["players"].items()
        if pd["alive"]
    ]

    if len(alive_players) <= 1:
        winner = "mafia" if any(pd["role"].team == "mafia" for pd in game["players"].values() if pd["alive"]) else "town"
        await end_game(game_id, chat_id, winner)
        await bot.session.close()
        return

    await db.reset_votes(game_id)
    for uid in game["players"]:
        game["players"][uid]["voted"] = False
        game["players"][uid]["vote_target"] = None

    await db.update_game_status(game_id, "voting", "voting")
    game["phase"] = "voting"

    await bot.send_message(
        chat_id,
        VOTE_START,
        reply_markup=vote_kb(alive_players, game_id),
    )

    game_timers[game_id] = asyncio.create_task(vote_timer(game_id, chat_id, bot))


async def vote_timer(game_id: int, chat_id: int, bot):
    await asyncio.sleep(VOTE_TIME)
    game = active_games.get(game_id)
    if not game or game["phase"] != "voting":
        return

    await resolve_votes(game_id, chat_id, bot)


async def resolve_votes(game_id: int, chat_id: int, bot=None):
    from aiogram import Bot
    from config import BOT_TOKEN
    if bot is None:
        bot = Bot(token=BOT_TOKEN)

    game = active_games.get(game_id)
    if not game:
        await bot.session.close()
        return

    vote_counts = {}
    for uid, pd in game["players"].items():
        if pd["voted"] and pd["vote_target"] and pd["alive"]:
            target = pd["vote_target"]
            vote_counts[target] = vote_counts.get(target, 0) + 1

    if not vote_counts:
        await bot.send_message(chat_id, VOTE_TIED)
        await start_next_night(game_id, chat_id, bot)
        return

    max_votes = max(vote_counts.values())
    top_players = [uid for uid, count in vote_counts.items() if count == max_votes]

    if len(top_players) > 1:
        await bot.send_message(chat_id, VOTE_TIED)
        await start_next_night(game_id, chat_id, bot)
        return

    eliminated_id = top_players[0]
    if eliminated_id not in game["players"]:
        await start_next_night(game_id, chat_id, bot)
        return

    game["players"][eliminated_id]["alive"] = False
    await db.kill_player(game_id, eliminated_id)
    role = game["players"][eliminated_id]["role"]

    elim_text = PLAYER_ELIMINATED.format(
        player=game["players"][eliminated_id].get("name", f"ID{eliminated_id}"),
        role=role.full_name(),
        dramatic_text=generate_death_story(role.name),
    )
    await bot.send_message(chat_id, elim_text)

    await db.record_event(
        game_id, "elimination",
        f"{game['players'][eliminated_id].get('name', f'ID{eliminated_id}')} ({role.full_name()}) ovoz berish orqali chiqarildi",
    )

    winner = check_win_condition([
        {"user_id": uid, "team": pd["role"].team, "alive": pd["alive"]}
        for uid, pd in game["players"].items()
    ])

    if winner:
        await end_game(game_id, chat_id, winner, bot)
        return

    await start_next_night(game_id, chat_id, bot)


async def start_next_night(game_id: int, chat_id: int, bot=None):
    from aiogram import Bot
    from config import BOT_TOKEN
    if bot is None:
        bot = Bot(token=BOT_TOKEN)

    game = active_games.get(game_id)
    if not game:
        await bot.session.close()
        return

    game["night"] += 1
    await db.update_game_status(game_id, "night", "night")
    game["phase"] = "night"

    await bot.send_message(chat_id, NIGHT_START.format(night=game["night"]))

    for user_id, pdata in game["players"].items():
        if not pdata["alive"]:
            continue
        pdata["night_action"] = None
        role = pdata["role"]
        try:
            if role.night_action:
                alive_others = [
                    {"user_id": uid, "username": game["players"][uid].get("name", f"ID{uid}")}
                    for uid, pd in game["players"].items()
                    if pd["alive"] and uid != user_id
                ]
                if role.team == "mafia" and role.action_type == "kill":
                    non_mafia = [p for p in alive_others if game["players"][p["user_id"]]["role"].team != "mafia"]
                    if non_mafia:
                        await bot.send_message(
                            user_id,
                            f"{role.full_name()}\n\nKimni o'ldiramiz?",
                            reply_markup=player_list_kb(non_mafia, f"mafia_kill:{game_id}"),
                        )
                elif role.action_type == "heal":
                    await bot.send_message(
                        user_id,
                        NIGHT_ACTION_PROMPT.format(role=role.full_name(), description=role.description),
                        reply_markup=player_list_kb(alive_others, f"heal:{game_id}"),
                    )
                elif role.action_type == "investigate":
                    await bot.send_message(
                        user_id,
                        NIGHT_ACTION_PROMPT.format(role=role.full_name(), description=role.description),
                        reply_markup=player_list_kb(alive_others, f"investigate:{game_id}"),
                    )
                else:
                    await bot.send_message(user_id, NIGHT_WAIT)
            else:
                await bot.send_message(user_id, NIGHT_WAIT)
        except Exception:
            pass

    game["phase"] = "night_action"
    game_timers[game_id] = asyncio.create_task(night_timer(game_id, chat_id))


async def end_game(game_id: int, chat_id: int, winner: str, bot=None):
    from aiogram import Bot
    from config import BOT_TOKEN
    if bot is None:
        bot = Bot(token=BOT_TOKEN)

    game = active_games.get(game_id)
    await db.end_game(game_id)

    for uid, pd in game["players"].items():
        role_team = pd["role"].team
        won = (winner == role_team) or (winner == "neutral" and role_team == "neutral")
        await db.update_player_stats(uid, won, role_team, pd["role"].name)
        if won:
            await db.add_achievement(uid, "🎯 Birinchi g'alaba")
        player_data = await db.get_player(uid)
        if player_data and player_data["games_played"] == 10:
            await db.add_achievement(uid, "🔱 10 ta o'yin")

    stats_text = ""
    for uid, pd in game["players"].items():
        status = "✅ Tirik" if pd["alive"] else "💀 O'lik"
        stats_text += f"{pd['role'].short_name()} — {pd.get('name', f'ID{uid}')} {status}\n"

    if winner == "mafia":
        msg = GAME_OVER_MAFIA.format(stats=stats_text)
    elif winner == "town":
        msg = GAME_OVER_TOWN.format(stats=stats_text)
    else:
        msg = GAME_OVER_NEUTRAL.format(winner="Neytral kuch", stats=stats_text)

    await bot.send_message(chat_id, msg, reply_markup=end_game_kb())

    active_games.pop(game_id, None)
    game_timers.pop(game_id, None)
    await db.close()


@router.callback_query(F.data.startswith("join_game:"))
async def handle_join_game(callback: CallbackQuery):
    game_id = int(callback.data.split(":")[1])
    game = active_games.get(game_id)
    if not game or game["phase"] != "lobby":
        await callback.answer(GAME_NOT_FOUND, show_alert=True)
        return

    user_id = callback.from_user.id
    if user_id in game["players"]:
        await callback.answer(ALREADY_JOINED, show_alert=True)
        return

    if len(game["players"]) >= MAX_PLAYERS:
        await callback.answer(GAME_FULL.format(max=MAX_PLAYERS), show_alert=True)
        return

    name = callback.from_user.first_name or f"ID{user_id}"
    game["players"][user_id] = {
        "name": name,
        "alive": True,
        "voted": False,
        "vote_target": None,
        "night_action": None,
    }

    await db.create_player(user_id, callback.from_user.username or "", name)
    await db.add_player_to_game(game_id, user_id)

    player_names = [
        f"• {pd['name']}" for pd in game["players"].values()
    ]

    try:
        await callback.message.edit_text(
            PLAYER_JOINED.format(
                name=name,
                count=len(game["players"]),
                max=MAX_PLAYERS,
                players="\n".join(player_names),
                time=GAME_JOIN_TIME,
            ),
            reply_markup=join_game_kb(game_id),
        )
    except TelegramBadRequest:
        pass

    await callback.answer(f"✅ O'yinga qo'shildingiz!")


@router.callback_query(F.data.startswith("leave_game:"))
async def handle_leave_game(callback: CallbackQuery):
    game_id = int(callback.data.split(":")[1])
    game = active_games.get(game_id)
    if not game:
        await callback.answer(GAME_NOT_FOUND, show_alert=True)
        return

    user_id = callback.from_user.id
    if user_id not in game["players"]:
        await callback.answer(NOT_IN_GAME, show_alert=True)
        return

    name = game["players"][user_id].get("name", f"ID{user_id}")
    del game["players"][user_id]

    await callback.message.answer(LEFT_GAME.format(player=name))
    await callback.answer(LEAVE_GAME)


@router.callback_query(F.data.startswith("force_start:"))
async def handle_force_start(callback: CallbackQuery):
    game_id = int(callback.data.split(":")[1])
    game = active_games.get(game_id)
    if not game:
        await callback.answer(GAME_NOT_FOUND, show_alert=True)
        return

    chat_id = game["chat_id"]
    member = await callback.message.chat.get_member(callback.from_user.id)
    if member.status not in ("creator", "administrator"):
        await callback.answer(ADMIN_ONLY, show_alert=True)
        return

    if len(game["players"]) < MIN_PLAYERS:
        await callback.answer(NOT_ENOUGH_PLAYERS.format(count=len(game["players"])), show_alert=True)
        return

    await callback.answer("👑 Majburiy start!")
    await callback.message.answer(FORCE_START)
    await start_game(game_id, chat_id)


@router.message(Command("leave"))
async def cmd_leave(message: Message):
    user_id = message.from_user.id
    for game_id, game in list(active_games.items()):
        if user_id in game["players"]:
            name = game["players"][user_id].get("name", f"ID{user_id}")
            del game["players"][user_id]
            await message.answer(LEAVE_GAME)
            if game.get("chat_id"):
                from aiogram import Bot
                from config import BOT_TOKEN
                bot = Bot(token=BOT_TOKEN)
                await bot.send_message(game["chat_id"], LEFT_GAME.format(player=name))
                await bot.session.close()
            return
    await message.answer(NOT_IN_GAME)


@router.callback_query(F.data == "rematch")
async def handle_rematch(callback: CallbackQuery):
    await callback.message.edit_text(
        "Yangi o'yin boshlash uchun /startgame buyrug'ini yuboring.",
        reply_markup=None,
    )
    await callback.answer()
