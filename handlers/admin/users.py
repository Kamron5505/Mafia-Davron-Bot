from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from config import OWNER_ID
from database.db import Database
from keyboards.admin_kb import admin_users_kb, back_to_admin_kb, cancel_kb, confirm_kb
from utils.logger import send_log

router = Router()
db = Database()


class UserStates(StatesGroup):
    wait_ban_id = State()
    wait_ban_reason = State()
    wait_unban_id = State()
    wait_add_balance_id = State()
    wait_add_balance_amount = State()
    wait_remove_balance_id = State()
    wait_remove_balance_amount = State()
    wait_userinfo_id = State()
    wait_resetstats_id = State()


def is_owner(user_id: int) -> bool:
    return user_id == OWNER_ID


@router.callback_query(F.data == "admin:users")
async def admin_users_menu(callback: CallbackQuery):
    if not is_owner(callback.from_user.id):
        await callback.answer("❌ Ruxsat yo'q!", show_alert=True)
        return
    await callback.message.edit_text(
        "👤 *FOYDALANUVCHILAR BOSHQARUVI*\n\nKerakli amalni tanlang:",
        reply_markup=admin_users_kb(),
    )
    await callback.answer()


@router.callback_query(F.data == "admin_user:ban")
async def ban_prompt(callback: CallbackQuery, state: FSMContext):
    if not is_owner(callback.from_user.id):
        await callback.answer("❌ Ruxsat yo'q!", show_alert=True)
        return
    await state.set_state(UserStates.wait_ban_id)
    await callback.message.edit_text(
        "🚫 Bloklash uchun foydalanuvchi ID sini yuboring:",
        reply_markup=cancel_kb(),
    )
    await callback.answer()


@router.message(StateFilter(UserStates.wait_ban_id))
async def process_ban_id(message: Message, state: FSMContext):
    if not is_owner(message.from_user.id):
        return
    try:
        user_id = int(message.text.strip())
        await state.update_data(ban_user_id=user_id)
        await state.set_state(UserStates.wait_ban_reason)
        await message.answer(
            "📝 Bloklash sababini yozing (yoki \"-\" ni yuboring):",
            reply_markup=cancel_kb(),
        )
    except ValueError:
        await message.answer("❌ Noto'g'ri ID.", reply_markup=cancel_kb())
        await state.clear()


@router.message(StateFilter(UserStates.wait_ban_reason))
async def process_ban_reason(message: Message, state: FSMContext):
    if not is_owner(message.from_user.id):
        return
    data = await state.get_data()
    user_id = data["ban_user_id"]
    reason = message.text.strip() if message.text.strip() != "-" else ""
    await state.clear()

    await db.ban_user(user_id, reason)
    reason_text = reason or "Ko'rsatilmagan"
    await send_log("Ban", f"Foydalanuvchi {user_id} bloklandi. Sabab: {reason_text}", f"ID{message.from_user.id}")
    await message.answer(
        f"✅ Foydalanuvchi `{user_id}` bloklandi!\n"
        f"Sabab: {reason_text}",
        reply_markup=back_to_admin_kb(),
    )


@router.callback_query(F.data == "admin_user:unban")
async def unban_prompt(callback: CallbackQuery, state: FSMContext):
    if not is_owner(callback.from_user.id):
        await callback.answer("❌ Ruxsat yo'q!", show_alert=True)
        return
    await state.set_state(UserStates.wait_unban_id)
    await callback.message.edit_text(
        "🔓 Blokdan olish uchun foydalanuvchi ID sini yuboring:",
        reply_markup=cancel_kb(),
    )
    await callback.answer()


@router.message(StateFilter(UserStates.wait_unban_id))
async def process_unban(message: Message, state: FSMContext):
    if not is_owner(message.from_user.id):
        return
    try:
        user_id = int(message.text.strip())
        await state.clear()
        await db.unban_user(user_id)
        await send_log("Unban", f"Foydalanuvchi {user_id} blokdan olindi", f"ID{message.from_user.id}")
        await message.answer(f"✅ Foydalanuvchi `{user_id}` blokdan olindi!", reply_markup=back_to_admin_kb())
    except ValueError:
        await message.answer("❌ Noto'g'ri ID.", reply_markup=cancel_kb())
        await state.clear()


@router.callback_query(F.data == "admin_user:userinfo")
async def userinfo_prompt(callback: CallbackQuery, state: FSMContext):
    if not is_owner(callback.from_user.id):
        await callback.answer("❌ Ruxsat yo'q!", show_alert=True)
        return
    await state.set_state(UserStates.wait_userinfo_id)
    await callback.message.edit_text(
        "👤 Ma'lumot olish uchun foydalanuvchi ID sini yuboring:",
        reply_markup=cancel_kb(),
    )
    await callback.answer()


@router.message(StateFilter(UserStates.wait_userinfo_id))
async def process_userinfo(message: Message, state: FSMContext):
    if not is_owner(message.from_user.id):
        return
    try:
        user_id = int(message.text.strip())
        await state.clear()
        player = await db.get_player(user_id)
        if not player:
            await message.answer("❌ Foydalanuvchi topilmadi.", reply_markup=back_to_admin_kb())
            return

        ban_status = "Ha 🚫" if player["is_banned"] else "Yo'q ✅"
        reason = f"\nSabab: {player['ban_reason']}" if player["is_banned"] and player["ban_reason"] else ""
        registered = player.get("registered_at", "") or "Noma'lum"
        if registered and isinstance(registered, str):
            registered = registered[:10]

        text = (
            f"👤 *FOYDALANUVCHI MA'LUMOTI*\n"
            f"———————————————\n"
            f"🆔 ID: `{player['user_id']}`\n"
            f"📛 Ism: {player['first_name'] or '—'}\n"
            f"🌐 Username: @{player['username'] if player['username'] else '—'}\n"
            f"⭐ Stars balansi: {player['stars_balance']}\n"
            f"🎮 O'yinlar: {player['games_played']} | 🏆 G'alabalar: {player['wins']}\n"
            f"📅 Ro'yxatdan o'tgan: {registered}\n"
            f"🚫 Ban holati: {ban_status}{reason}"
        )
        await message.answer(text, reply_markup=back_to_admin_kb())
    except ValueError:
        await message.answer("❌ Noto'g'ri ID.", reply_markup=cancel_kb())
        await state.clear()


@router.callback_query(F.data == "admin_user:addstars")
async def add_balance_prompt(callback: CallbackQuery, state: FSMContext):
    if not is_owner(callback.from_user.id):
        await callback.answer("❌ Ruxsat yo'q!", show_alert=True)
        return
    await state.set_state(UserStates.wait_add_balance_id)
    await callback.message.edit_text(
        "⭐ Balans oshirish uchun foydalanuvchi ID sini yuboring:",
        reply_markup=cancel_kb(),
    )
    await callback.answer()


@router.message(StateFilter(UserStates.wait_add_balance_id))
async def process_add_balance_id(message: Message, state: FSMContext):
    if not is_owner(message.from_user.id):
        return
    try:
        user_id = int(message.text.strip())
        await state.update_data(balance_user_id=user_id)
        await state.set_state(UserStates.wait_add_balance_amount)
        await message.answer("⭐ Qancha Stars qo'shish kerak?", reply_markup=cancel_kb())
    except ValueError:
        await message.answer("❌ Noto'g'ri ID.", reply_markup=cancel_kb())
        await state.clear()


@router.message(StateFilter(UserStates.wait_add_balance_amount))
async def process_add_balance_amount(message: Message, state: FSMContext):
    if not is_owner(message.from_user.id):
        return
    try:
        amount = int(message.text.strip())
        if amount <= 0:
            await message.answer("❌ Musbat son kiriting.", reply_markup=cancel_kb())
            return
        data = await state.get_data()
        user_id = data["balance_user_id"]
        await state.clear()

        await db.add_stars(user_id, amount)
        await db.add_stars_log(user_id, amount, "admin_add", "Admin tomonidan qo'shilgan", message.from_user.id)
        new_balance = await db.get_stars_balance(user_id)
        await send_log("Stars qo'shish", f"Foydalanuvchi {user_id}: +{amount}⭐ (Balans: {new_balance})", f"ID{message.from_user.id}")
        await message.answer(
            f"✅ Foydalanuvchi `{user_id}` ga {amount}⭐ qo'shildi!\n"
            f"Yangi balans: {new_balance}⭐",
            reply_markup=back_to_admin_kb(),
        )
    except ValueError:
        await message.answer("❌ Noto'g'ri miqdor.", reply_markup=cancel_kb())
        await state.clear()


@router.callback_query(F.data == "admin_user:removestars")
async def remove_balance_prompt(callback: CallbackQuery, state: FSMContext):
    if not is_owner(callback.from_user.id):
        await callback.answer("❌ Ruxsat yo'q!", show_alert=True)
        return
    await state.set_state(UserStates.wait_remove_balance_id)
    await callback.message.edit_text(
        "➖ Balans kamaytirish uchun foydalanuvchi ID sini yuboring:",
        reply_markup=cancel_kb(),
    )
    await callback.answer()


@router.message(StateFilter(UserStates.wait_remove_balance_id))
async def process_remove_balance_id(message: Message, state: FSMContext):
    if not is_owner(message.from_user.id):
        return
    try:
        user_id = int(message.text.strip())
        await state.update_data(remove_user_id=user_id)
        await state.set_state(UserStates.wait_remove_balance_amount)
        await message.answer("➖ Qancha Stars kamaytirish kerak?", reply_markup=cancel_kb())
    except ValueError:
        await message.answer("❌ Noto'g'ri ID.", reply_markup=cancel_kb())
        await state.clear()


@router.message(StateFilter(UserStates.wait_remove_balance_amount))
async def process_remove_balance_amount(message: Message, state: FSMContext):
    if not is_owner(message.from_user.id):
        return
    try:
        amount = int(message.text.strip())
        if amount <= 0:
            await message.answer("❌ Musbat son kiriting.", reply_markup=cancel_kb())
            return
        data = await state.get_data()
        user_id = data["remove_user_id"]
        await state.clear()

        await db.remove_stars(user_id, amount)
        await db.add_stars_log(user_id, amount, "admin_remove", "Admin tomonidan kamaytirilgan", message.from_user.id)
        new_balance = await db.get_stars_balance(user_id)
        await send_log("Stars kamaytirish", f"Foydalanuvchi {user_id}: -{amount}⭐ (Balans: {new_balance})", f"ID{message.from_user.id}")
        await message.answer(
            f"✅ Foydalanuvchi `{user_id}` dan {amount}⭐ kamaytirildi!\n"
            f"Yangi balans: {new_balance}⭐",
            reply_markup=back_to_admin_kb(),
        )
    except ValueError:
        await message.answer("❌ Noto'g'ri miqdor.", reply_markup=cancel_kb())
        await state.clear()


@router.callback_query(F.data == "admin_user:resetstats")
async def reset_stats_prompt(callback: CallbackQuery, state: FSMContext):
    if not is_owner(callback.from_user.id):
        await callback.answer("❌ Ruxsat yo'q!", show_alert=True)
        return
    await state.set_state(UserStates.wait_resetstats_id)
    await callback.message.edit_text(
        "🔄 Statistikani nolga tushirish uchun foydalanuvchi ID sini yuboring:",
        reply_markup=cancel_kb(),
    )
    await callback.answer()


@router.message(StateFilter(UserStates.wait_resetstats_id))
async def process_reset_stats(message: Message, state: FSMContext):
    if not is_owner(message.from_user.id):
        return
    try:
        user_id = int(message.text.strip())
        await state.clear()
        await db.reset_player_stats(user_id)
        await send_log("Statistika reset", f"Foydalanuvchi {user_id} statistikasi nolga tushirildi", f"ID{message.from_user.id}")
        await message.answer(f"✅ Foydalanuvchi `{user_id}` statistikasi nolga tushirildi!", reply_markup=back_to_admin_kb())
    except ValueError:
        await message.answer("❌ Noto'g'ri ID.", reply_markup=cancel_kb())
        await state.clear()


@router.callback_query(F.data == "admin_user:allban")
async def all_ban_prompt(callback: CallbackQuery):
    if not is_owner(callback.from_user.id):
        await callback.answer("❌ Ruxsat yo'q!", show_alert=True)
        return
    count = await db.get_players_count()
    await callback.message.edit_text(
        f"⚠️ *Barcha foydalanuvchilarni bloklash*\n\n"
        f"Jami {count} ta foydalanuvchi bloklanadi.\n"
        f"Bu amalni tasdiqlaysizmi?",
        reply_markup=confirm_kb("all_ban"),
    )
    await callback.answer()


@router.callback_query(F.data == "confirm:all_ban")
async def confirm_all_ban(callback: CallbackQuery):
    if not is_owner(callback.from_user.id):
        await callback.answer("❌ Ruxsat yo'q!", show_alert=True)
        return
    players = await db.get_all_players()
    count = 0
    for p in players:
        if not p["is_banned"]:
            await db.ban_user(p["user_id"], "Ommaviy bloklash")
            count += 1
    await send_log("Ommaviy ban", f"{count} ta foydalanuvchi bloklandi", f"ID{callback.from_user.id}")
    await callback.message.edit_text(
        f"✅ {count} ta foydalanuvchi bloklandi!",
        reply_markup=back_to_admin_kb(),
    )
    await callback.answer()


@router.callback_query(F.data.startswith("confirm:cancel"))
async def confirm_cancel(callback: CallbackQuery):
    await callback.message.edit_text("❌ Amal bekor qilindi.", reply_markup=back_to_admin_kb())
    await callback.answer()


@router.message(Command("ban"))
async def cmd_ban(message: Message):
    if not is_owner(message.from_user.id):
        return
    args = message.text.split(maxsplit=2)
    if len(args) < 2:
        await message.answer("❌ /ban <user_id> [sabab]")
        return
    try:
        user_id = int(args[1])
        reason = args[2] if len(args) > 2 else ""
        await db.ban_user(user_id, reason)
        await send_log("Ban", f"Foydalanuvchi {user_id} bloklandi. Sabab: {reason or '—'}", f"ID{message.from_user.id}")
        await message.answer(f"✅ `{user_id}` bloklandi!")
    except ValueError:
        await message.answer("❌ Noto'g'ri ID.")


@router.message(Command("unban"))
async def cmd_unban(message: Message):
    if not is_owner(message.from_user.id):
        return
    args = message.text.split()
    if len(args) < 2:
        await message.answer("❌ /unban <user_id>")
        return
    try:
        user_id = int(args[1])
        await db.unban_user(user_id)
        await send_log("Unban", f"Foydalanuvchi {user_id} blokdan olindi", f"ID{message.from_user.id}")
        await message.answer(f"✅ `{user_id}` blokdan olindi!")
    except ValueError:
        await message.answer("❌ Noto'g'ri ID.")


@router.message(Command("addbalance"))
async def cmd_add_balance(message: Message):
    if not is_owner(message.from_user.id):
        return
    args = message.text.split()
    if len(args) < 3:
        await message.answer("❌ /addbalance <user_id> <miqdor>")
        return
    try:
        user_id = int(args[1])
        amount = int(args[2])
        await db.add_stars(user_id, amount)
        await db.add_stars_log(user_id, amount, "admin_add", "Admin tomonidan qo'shilgan", message.from_user.id)
        await send_log("Stars qo'shish", f"Foydalanuvchi {user_id}: +{amount}⭐", f"ID{message.from_user.id}")
        await message.answer(f"✅ `{user_id}` ga {amount}⭐ qo'shildi!")
    except ValueError:
        await message.answer("❌ Noto'g'ri format.")


@router.message(Command("removebalance"))
async def cmd_remove_balance(message: Message):
    if not is_owner(message.from_user.id):
        return
    args = message.text.split()
    if len(args) < 3:
        await message.answer("❌ /removebalance <user_id> <miqdor>")
        return
    try:
        user_id = int(args[1])
        amount = int(args[2])
        await db.remove_stars(user_id, amount)
        await db.add_stars_log(user_id, amount, "admin_remove", "Admin tomonidan kamaytirilgan", message.from_user.id)
        await send_log("Stars kamaytirish", f"Foydalanuvchi {user_id}: -{amount}⭐", f"ID{message.from_user.id}")
        await message.answer(f"✅ `{user_id}` dan {amount}⭐ kamaytirildi!")
    except ValueError:
        await message.answer("❌ Noto'g'ri format.")


@router.message(Command("userinfo"))
async def cmd_userinfo(message: Message):
    if not is_owner(message.from_user.id):
        return
    args = message.text.split()
    if len(args) < 2:
        await message.answer("❌ /userinfo <user_id>")
        return
    try:
        user_id = int(args[1])
        player = await db.get_player(user_id)
        if not player:
            await message.answer("❌ Foydalanuvchi topilmadi.")
            return
        ban_status = "Ha 🚫" if player["is_banned"] else "Yo'q ✅"
        reason = f"\nSabab: {player['ban_reason']}" if player["is_banned"] and player["ban_reason"] else ""
        registered = player.get("registered_at", "") or "Noma'lum"
        if registered and isinstance(registered, str):
            registered = registered[:10]
        text = (
            f"👤 *FOYDALANUVCHI MA'LUMOTI*\n"
            f"🆔 ID: `{user_id}`\n"
            f"📛 Ism: {player['first_name'] or '—'}\n"
            f"🌐 Username: @{player['username'] if player['username'] else '—'}\n"
            f"⭐ Stars balansi: {player['stars_balance']}\n"
            f"🎮 O'yinlar: {player['games_played']} | 🏆 G'alabalar: {player['wins']}\n"
            f"📅 Ro'yxatdan o'tgan: {registered}\n"
            f"🚫 Ban holati: {ban_status}{reason}"
        )
        await message.answer(text)
    except ValueError:
        await message.answer("❌ Noto'g'ri ID.")


@router.message(Command("resetstats"))
async def cmd_reset_stats(message: Message):
    if not is_owner(message.from_user.id):
        return
    args = message.text.split()
    if len(args) < 2:
        await message.answer("❌ /resetstats <user_id>")
        return
    try:
        user_id = int(args[1])
        await db.reset_player_stats(user_id)
        await send_log("Statistika reset", f"Foydalanuvchi {user_id} statistikasi nolga tushirildi", f"ID{message.from_user.id}")
        await message.answer(f"✅ `{user_id}` statistikasi nolga tushirildi!")
    except ValueError:
        await message.answer("❌ Noto'g'ri ID.")


@router.message(Command("allban"))
async def cmd_all_ban(message: Message):
    if not is_owner(message.from_user.id):
        return
    players = await db.get_all_players()
    count = 0
    for p in players:
        if not p["is_banned"]:
            await db.ban_user(p["user_id"], "Ommaviy bloklash")
            count += 1
    await send_log("Ommaviy ban", f"{count} ta foydalanuvchi bloklandi", f"ID{message.from_user.id}")
    await message.answer(f"✅ {count} ta foydalanuvchi bloklandi!")
