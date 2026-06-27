from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from config import OWNER_ID
from database.db import Database
from keyboards.admin_kb import admin_stars_kb, back_to_admin_kb, cancel_kb
from utils.logger import send_log

router = Router()
db = Database()


class StarsStates(StatesGroup):
    wait_add_id = State()
    wait_add_amount = State()
    wait_remove_id = State()
    wait_remove_amount = State()
    wait_log_id = State()


def is_owner(user_id: int) -> bool:
    return user_id == OWNER_ID


@router.callback_query(F.data == "admin:stars")
async def admin_stars_menu(callback: CallbackQuery):
    if not is_owner(callback.from_user.id):
        await callback.answer("❌ Ruxsat yo'q!", show_alert=True)
        return
    await callback.message.edit_text(
        "⭐ *STARS BOSHQARUVI*\n\nKerakli amalni tanlang:",
        reply_markup=admin_stars_kb(),
    )
    await callback.answer()


@router.callback_query(F.data == "admin_stars:add")
async def stars_add_prompt(callback: CallbackQuery, state: FSMContext):
    if not is_owner(callback.from_user.id):
        await callback.answer("❌ Ruxsat yo'q!", show_alert=True)
        return
    await state.set_state(StarsStates.wait_add_id)
    await callback.message.edit_text(
        "⭐ Stars qo'shish uchun foydalanuvchi ID sini yuboring:",
        reply_markup=cancel_kb(),
    )
    await callback.answer()


@router.message(StateFilter(StarsStates.wait_add_id))
async def process_stars_add_id(message: Message, state: FSMContext):
    if not is_owner(message.from_user.id):
        return
    try:
        user_id = int(message.text.strip())
        await state.update_data(target_id=user_id)
        await state.set_state(StarsStates.wait_add_amount)
        await message.answer("⭐ Qancha Stars qo'shish kerak?", reply_markup=cancel_kb())
    except ValueError:
        await message.answer("❌ Noto'g'ri ID.", reply_markup=cancel_kb())
        await state.clear()


@router.message(StateFilter(StarsStates.wait_add_amount))
async def process_stars_add_amount(message: Message, state: FSMContext):
    if not is_owner(message.from_user.id):
        return
    try:
        amount = int(message.text.strip())
        if amount <= 0:
            await message.answer("❌ Musbat son kiriting.", reply_markup=cancel_kb())
            return
        data = await state.get_data()
        user_id = data["target_id"]
        await state.clear()

        await db.add_stars(user_id, amount)
        await db.add_stars_log(user_id, amount, "admin_add", "Admin tomonidan qo'shilgan", message.from_user.id)
        new_balance = await db.get_stars_balance(user_id)
        await send_log("Stars qo'shish", f"Foydalanuvchi {user_id}: +{amount}⭐ (Balans: {new_balance})", f"ID{message.from_user.id}")
        await message.answer(
            f"✅ `{user_id}` ga {amount}⭐ qo'shildi!\nYangi balans: {new_balance}⭐",
            reply_markup=back_to_admin_kb(),
        )
    except ValueError:
        await message.answer("❌ Noto'g'ri miqdor.", reply_markup=cancel_kb())
        await state.clear()


@router.callback_query(F.data == "admin_stars:remove")
async def stars_remove_prompt(callback: CallbackQuery, state: FSMContext):
    if not is_owner(callback.from_user.id):
        await callback.answer("❌ Ruxsat yo'q!", show_alert=True)
        return
    await state.set_state(StarsStates.wait_remove_id)
    await callback.message.edit_text(
        "➖ Stars kamaytirish uchun foydalanuvchi ID sini yuboring:",
        reply_markup=cancel_kb(),
    )
    await callback.answer()


@router.message(StateFilter(StarsStates.wait_remove_id))
async def process_stars_remove_id(message: Message, state: FSMContext):
    if not is_owner(message.from_user.id):
        return
    try:
        user_id = int(message.text.strip())
        await state.update_data(target_id=user_id)
        await state.set_state(StarsStates.wait_remove_amount)
        await message.answer("➖ Qancha Stars kamaytirish kerak?", reply_markup=cancel_kb())
    except ValueError:
        await message.answer("❌ Noto'g'ri ID.", reply_markup=cancel_kb())
        await state.clear()


@router.message(StateFilter(StarsStates.wait_remove_amount))
async def process_stars_remove_amount(message: Message, state: FSMContext):
    if not is_owner(message.from_user.id):
        return
    try:
        amount = int(message.text.strip())
        if amount <= 0:
            await message.answer("❌ Musbat son kiriting.", reply_markup=cancel_kb())
            return
        data = await state.get_data()
        user_id = data["target_id"]
        await state.clear()

        await db.remove_stars(user_id, amount)
        await db.add_stars_log(user_id, amount, "admin_remove", "Admin tomonidan kamaytirilgan", message.from_user.id)
        new_balance = await db.get_stars_balance(user_id)
        await send_log("Stars kamaytirish", f"Foydalanuvchi {user_id}: -{amount}⭐ (Balans: {new_balance})", f"ID{message.from_user.id}")
        await message.answer(
            f"✅ `{user_id}` dan {amount}⭐ kamaytirildi!\nYangi balans: {new_balance}⭐",
            reply_markup=back_to_admin_kb(),
        )
    except ValueError:
        await message.answer("❌ Noto'g'ri miqdor.", reply_markup=cancel_kb())
        await state.clear()


@router.callback_query(F.data == "admin_stars:log")
async def stars_log_prompt(callback: CallbackQuery, state: FSMContext):
    if not is_owner(callback.from_user.id):
        await callback.answer("❌ Ruxsat yo'q!", show_alert=True)
        return
    await state.set_state(StarsStates.wait_log_id)
    await callback.message.edit_text(
        "📜 Stars tarixini ko'rish uchun foydalanuvchi ID sini yuboring:",
        reply_markup=cancel_kb(),
    )
    await callback.answer()


@router.message(StateFilter(StarsStates.wait_log_id))
async def process_stars_log(message: Message, state: FSMContext):
    if not is_owner(message.from_user.id):
        return
    try:
        user_id = int(message.text.strip())
        await state.clear()
        log_entries = await db.get_stars_log(user_id)
        if not log_entries:
            await message.answer("❌ Stars tarixi topilmadi.", reply_markup=back_to_admin_kb())
            return

        text = f"📜 *Stars tarixi — `{user_id}`*\n\n"
        for entry in log_entries[:20]:
            amount = entry["amount"]
            sign = "+" if entry["action_type"] in ("purchase", "admin_add") else "-"
            text += f"• {sign}{amount}⭐ — {entry['action_type']}\n  🕐 {entry['created_at'][:19]}\n"
        await message.answer(text, reply_markup=back_to_admin_kb())
    except ValueError:
        await message.answer("❌ Noto'g'ri ID.", reply_markup=cancel_kb())
        await state.clear()


@router.callback_query(F.data == "admin_stars:pending")
async def pending_payments(callback: CallbackQuery):
    if not is_owner(callback.from_user.id):
        await callback.answer("❌ Ruxsat yo'q!", show_alert=True)
        return
    payments = await db.get_pending_payments()
    if not payments:
        await callback.message.edit_text("✅ Kutilayotgan to'lovlar yo'q.", reply_markup=back_to_admin_kb())
        await callback.answer()
        return

    text = "💳 *Kutilayotgan to'lovlar:*\n\n"
    for p in payments:
        text += f"🆔 #{p['id']} | Foydalanuvchi: {p['user_id']}\n  ⭐ {p['stars_amount']} | {p['price_amount']} {p['currency']}\n  🕐 {p['created_at'][:19]}\n\n"
    await callback.message.edit_text(text, reply_markup=back_to_admin_kb())
    await callback.answer()


@router.callback_query(F.data == "admin_stars:total")
async def total_stars_stats(callback: CallbackQuery):
    if not is_owner(callback.from_user.id):
        await callback.answer("❌ Ruxsat yo'q!", show_alert=True)
        return
    total_sold = await db.get_total_stars_sold()
    total_revenue = await db.get_total_revenue()
    text = (
        "📊 *Umumiy Stars statistikasi:*\n"
        f"———————————————\n"
        f"⭐ Jami sotilgan Stars: {total_sold}\n"
        f"💰 Daromad: ~${total_revenue}"
    )
    await callback.message.edit_text(text, reply_markup=back_to_admin_kb())
    await callback.answer()


@router.message(Command("addstars"))
async def cmd_add_stars(message: Message):
    if not is_owner(message.from_user.id):
        return
    args = message.text.split()
    if len(args) < 3:
        await message.answer("❌ /addstars <user_id> <amount>")
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


@router.message(Command("removestars"))
async def cmd_remove_stars(message: Message):
    if not is_owner(message.from_user.id):
        return
    args = message.text.split()
    if len(args) < 3:
        await message.answer("❌ /removestars <user_id> <amount>")
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


@router.message(Command("starslog"))
async def cmd_stars_log(message: Message):
    if not is_owner(message.from_user.id):
        return
    args = message.text.split()
    if len(args) < 2:
        await message.answer("❌ /starslog <user_id>")
        return
    try:
        user_id = int(args[1])
        log_entries = await db.get_stars_log(user_id)
        if not log_entries:
            await message.answer(f"❌ `{user_id}` uchun Stars tarixi topilmadi.")
            return
        text = f"📜 *Stars tarixi — `{user_id}`*\n\n"
        for entry in log_entries[:20]:
            amount = entry["amount"]
            sign = "+" if entry["action_type"] in ("purchase", "admin_add") else "-"
            text += f"• {sign}{amount}⭐ — {entry['action_type']}\n  🕐 {entry['created_at'][:19]}\n"
        await message.answer(text)
    except ValueError:
        await message.answer("❌ Noto'g'ri ID.")


@router.message(Command("totalstars"))
async def cmd_total_stars(message: Message):
    if not is_owner(message.from_user.id):
        return
    total_sold = await db.get_total_stars_sold()
    total_revenue = await db.get_total_revenue()
    await message.answer(
        f"📊 *Stars statistikasi:*\n"
        f"⭐ Jami sotilgan: {total_sold}\n"
        f"💰 Daromad: ~${total_revenue}"
    )


@router.message(Command("pendingpayments"))
async def cmd_pending_payments(message: Message):
    if not is_owner(message.from_user.id):
        return
    payments = await db.get_pending_payments()
    if not payments:
        await message.answer("✅ Kutilayotgan to'lovlar yo'q.")
        return
    text = "💳 *Kutilayotgan to'lovlar:*\n\n"
    for p in payments:
        text += f"🆔 #{p['id']} | Foydalanuvchi: {p['user_id']}\n  ⭐ {p['stars_amount']} | {p['price_amount']}\n  🕐 {p['created_at'][:19]}\n\n"
    await message.answer(text)
