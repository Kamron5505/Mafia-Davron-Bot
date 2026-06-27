from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command
from config import OWNER_ID
from database.db import Database
from keyboards.admin_kb import admin_stats_kb, back_to_admin_kb

router = Router()
db = Database()


def is_owner(user_id: int) -> bool:
    return user_id == OWNER_ID


@router.callback_query(F.data == "admin:stats")
async def admin_stats(callback: CallbackQuery):
    if not is_owner(callback.from_user.id):
        await callback.answer("❌ Ruxsat yo'q!", show_alert=True)
        return
    text = await build_stats_text()
    await callback.message.edit_text(text, reply_markup=admin_stats_kb())
    await callback.answer()


@router.callback_query(F.data == "admin_stats:refresh")
async def refresh_stats(callback: CallbackQuery):
    if not is_owner(callback.from_user.id):
        await callback.answer("❌ Ruxsat yo'q!", show_alert=True)
        return
    text = await build_stats_text()
    await callback.message.edit_text(text, reply_markup=admin_stats_kb())
    await callback.answer()


async def build_stats_text() -> str:
    total_players = await db.get_players_count()
    active_today = await db.get_active_users_today()
    total_games = await db.get_total_games_played()
    total_stars = await db.get_total_stars_sold()
    total_revenue = await db.get_total_revenue()
    total_groups = await db.get_groups_count()
    banned_count = await db.get_banned_count()

    return (
        "📊 *BOT STATISTIKASI*\n"
        f"———————————————\n"
        f"👥 Jami foydalanuvchilar: {total_players:,}\n"
        f"🟢 Bugun faollar: {active_today}\n"
        f"🎮 O'tkazilgan o'yinlar: {total_games:,}\n"
        f"⭐ Sotilgan Stars: {total_stars:,}\n"
        f"💰 Daromad: ~${total_revenue:,}\n"
        f"🏘 Guruhlar soni: {total_groups}\n"
        f"🚫 Banlanganlar: {banned_count}"
    )


@router.message(Command("stats"))
async def cmd_stats(message: Message):
    if not is_owner(message.from_user.id):
        return

    chat = message.chat
    if chat.type != "private":
        from utils.state import active_games
        for gid, g in active_games.items():
            if g.get("chat_id") == chat.id and g["phase"] != "ended":
                from utils.messages import GAME_STATS
                alive = []
                dead = []
                for uid, pd in g["players"].items():
                    name = pd.get("name", f"ID{uid}")
                    entry = f"{pd['role'].short_name()} — {name}"
                    if pd["alive"]:
                        alive.append(entry)
                    else:
                        dead.append(entry)
                events = await db.get_events(gid)
                event_text = "\n".join(f"• {e['description']}" for e in events[-5:]) or "Hodisalar yo'q"
                text = GAME_STATS.format(
                    roles=", ".join(pd['role'].short_name() for pd in g["players"].values()),
                    events=event_text,
                    alive=len(alive),
                    alive_list="\n".join(alive) if alive else "—",
                    dead_list="\n".join(dead) if dead else "—",
                )
                await message.answer(text)
                return

        await message.answer("❌ Faol o'yin topilmadi.")
        return

    text = await build_stats_text()
    await message.answer(text, reply_markup=back_to_admin_kb())
