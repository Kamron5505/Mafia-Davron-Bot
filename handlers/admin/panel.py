from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from config import OWNER_ID, ADMIN_IDS, MIN_PLAYERS, MAX_PLAYERS, LOG_CHANNEL_ID
from database.db import Database
from keyboards.admin_kb import admin_panel_kb, admin_settings_kb, back_to_admin_kb, cancel_kb
from utils.logger import send_log

router = Router()
db = Database()


def is_owner(user_id: int) -> bool:
    return user_id == OWNER_ID


def is_admin(user_id: int) -> bool:
    return user_id == OWNER_ID or user_id in ADMIN_IDS


class SettingsStates(StatesGroup):
    wait_log_channel = State()
    wait_min_players = State()
    wait_max_players = State()
    wait_add_admin = State()
    wait_remove_admin = State()


@router.message(Command("admin"))
async def cmd_admin(message: Message):
    if not is_owner(message.from_user.id):
        await message.answer("❌ Bu buyruq faqat bot egasi uchun!")
        return
    await message.answer(
        "🛠 *ADMIN PANEL*\n\nQuyidagi bo'limlardan birini tanlang:",
        reply_markup=admin_panel_kb(),
    )


@router.callback_query(F.data == "admin:back")
async def back_to_admin(callback: CallbackQuery):
    if not is_owner(callback.from_user.id):
        await callback.answer("❌ Ruxsat yo'q!", show_alert=True)
        return
    await callback.message.edit_text(
        "🛠 *ADMIN PANEL*\n\nQuyidagi bo'limlardan birini tanlang:",
        reply_markup=admin_panel_kb(),
    )
    await callback.answer()


@router.callback_query(F.data == "admin:cancel")
async def cancel_action(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    await callback.message.edit_text("❌ Amal bekor qilindi.", reply_markup=back_to_admin_kb())
    await callback.answer()


@router.callback_query(F.data == "admin:settings")
async def admin_settings(callback: CallbackQuery):
    if not is_owner(callback.from_user.id):
        await callback.answer("❌ Ruxsat yo'q!", show_alert=True)
        return

    min_p = await db.get_setting("min_players", str(MIN_PLAYERS))
    max_p = await db.get_setting("max_players", str(MAX_PLAYERS))
    log_ch = await db.get_setting("log_channel_id", str(LOG_CHANNEL_ID))
    maint = await db.get_setting("maintenance", "off")
    admins = await db.get_setting("admin_ids", ", ".join(str(a) for a in ADMIN_IDS))

    text = (
        "⚙️ *SOZLAMALAR*\n"
        f"———————————————\n"
        f"📢 Log kanal: `{log_ch}`\n"
        f"👥 Min o'yinchilar: {min_p}\n"
        f"👥 Max o'yinchilar: {max_p}\n"
        f"🔧 Maintenance: {maint}\n"
        f"👑 Adminlar: {admins if admins else '—'}"
    )
    await callback.message.edit_text(text, reply_markup=admin_settings_kb())
    await callback.answer()


@router.callback_query(F.data == "admin_set:logchannel")
async def set_log_channel(callback: CallbackQuery, state: FSMContext):
    if not is_owner(callback.from_user.id):
        await callback.answer("❌ Ruxsat yo'q!", show_alert=True)
        return
    await state.set_state(SettingsStates.wait_log_channel)
    await callback.message.edit_text(
        "📢 Log kanal ID sini yuboring (masalan: -100123456789):\n\n"
        "Kanal ID sini olish uchun kanalingizga @getidsbot qo'shing.",
        reply_markup=cancel_kb(),
    )
    await callback.answer()


@router.message(StateFilter(SettingsStates.wait_log_channel))
async def process_log_channel(message: Message, state: FSMContext):
    if not is_owner(message.from_user.id):
        return
    try:
        channel_id = int(message.text.strip())
        await db.set_setting("log_channel_id", str(channel_id))
        await send_log("Sozlamalar", f"Log kanal o'rnatildi: {channel_id}", f"ID{message.from_user.id}")
        await message.answer(f"✅ Log kanal `{channel_id}` ga o'rnatildi!", reply_markup=back_to_admin_kb())
    except ValueError:
        await message.answer("❌ Noto'g'ri ID. Qaytadan urinib ko'ring.", reply_markup=cancel_kb())
        return
    await state.clear()


@router.callback_query(F.data == "admin_set:minplayers")
async def set_min_players(callback: CallbackQuery, state: FSMContext):
    if not is_owner(callback.from_user.id):
        await callback.answer("❌ Ruxsat yo'q!", show_alert=True)
        return
    await state.set_state(SettingsStates.wait_min_players)
    await callback.message.edit_text(
        "👥 Minimal o'yinchilar sonini yuboring (default: 6):",
        reply_markup=cancel_kb(),
    )
    await callback.answer()


@router.message(StateFilter(SettingsStates.wait_min_players))
async def process_min_players(message: Message, state: FSMContext):
    if not is_owner(message.from_user.id):
        return
    try:
        val = int(message.text.strip())
        if val < 3 or val > 30:
            await message.answer("❌ 3 dan 30 gacha son kiriting.", reply_markup=cancel_kb())
            return
        await db.set_setting("min_players", str(val))
        await send_log("Sozlamalar", f"Min o'yinchilar o'zgartirildi: {val}", f"ID{message.from_user.id}")
        await message.answer(f"✅ Minimal o'yinchilar {val} ga o'rnatildi!", reply_markup=back_to_admin_kb())
    except ValueError:
        await message.answer("❌ Noto'g'ri son.", reply_markup=cancel_kb())
        return
    await state.clear()


@router.callback_query(F.data == "admin_set:maxplayers")
async def set_max_players(callback: CallbackQuery, state: FSMContext):
    if not is_owner(callback.from_user.id):
        await callback.answer("❌ Ruxsat yo'q!", show_alert=True)
        return
    await state.set_state(SettingsStates.wait_max_players)
    await callback.message.edit_text(
        "👥 Maksimal o'yinchilar sonini yuboring (default: 30):",
        reply_markup=cancel_kb(),
    )
    await callback.answer()


@router.message(StateFilter(SettingsStates.wait_max_players))
async def process_max_players(message: Message, state: FSMContext):
    if not is_owner(message.from_user.id):
        return
    try:
        val = int(message.text.strip())
        if val < 3 or val > 50:
            await message.answer("❌ 3 dan 50 gacha son kiriting.", reply_markup=cancel_kb())
            return
        await db.set_setting("max_players", str(val))
        await send_log("Sozlamalar", f"Max o'yinchilar o'zgartirildi: {val}", f"ID{message.from_user.id}")
        await message.answer(f"✅ Maksimal o'yinchilar {val} ga o'rnatildi!", reply_markup=back_to_admin_kb())
    except ValueError:
        await message.answer("❌ Noto'g'ri son.", reply_markup=cancel_kb())
        return
    await state.clear()


@router.callback_query(F.data == "admin_set:maintenance")
async def toggle_maintenance(callback: CallbackQuery):
    if not is_owner(callback.from_user.id):
        await callback.answer("❌ Ruxsat yo'q!", show_alert=True)
        return
    current = await db.get_setting("maintenance", "off")
    new_val = "off" if current == "on" else "on"
    await db.set_setting("maintenance", new_val)
    status = "yoqildi 🔧" if new_val == "on" else "o'chirildi ✅"
    await send_log("Sozlamalar", f"Maintenance {status}", f"ID{callback.from_user.id}")
    await callback.message.edit_text(
        f"✅ Maintenance rejimi {status}!",
        reply_markup=back_to_admin_kb(),
    )
    await callback.answer()


@router.callback_query(F.data == "admin_set:addadmin")
async def add_admin_prompt(callback: CallbackQuery, state: FSMContext):
    if not is_owner(callback.from_user.id):
        await callback.answer("❌ Ruxsat yo'q!", show_alert=True)
        return
    await state.set_state(SettingsStates.wait_add_admin)
    await callback.message.edit_text(
        "👑 Admin qilish uchun foydalanuvchi ID sini yuboring:",
        reply_markup=cancel_kb(),
    )
    await callback.answer()


@router.message(StateFilter(SettingsStates.wait_add_admin))
async def process_add_admin(message: Message, state: FSMContext):
    if not is_owner(message.from_user.id):
        return
    try:
        uid = int(message.text.strip())
        global ADMIN_IDS
        if uid not in ADMIN_IDS:
            ADMIN_IDS.append(uid)
        await db.set_setting("admin_ids", ", ".join(str(a) for a in ADMIN_IDS))
        await send_log("Admin boshqaruvi", f"Admin qo'shildi: {uid}", f"ID{message.from_user.id}")
        await message.answer(f"✅ Foydalanuvchi {uid} admin qilindi!", reply_markup=back_to_admin_kb())
    except ValueError:
        await message.answer("❌ Noto'g'ri ID.", reply_markup=cancel_kb())
        return
    await state.clear()


@router.callback_query(F.data == "admin_set:removeadmin")
async def remove_admin_prompt(callback: CallbackQuery, state: FSMContext):
    if not is_owner(callback.from_user.id):
        await callback.answer("❌ Ruxsat yo'q!", show_alert=True)
        return
    await state.set_state(SettingsStates.wait_remove_admin)
    await callback.message.edit_text(
        "👑 Adminlikdan olish uchun foydalanuvchi ID sini yuboring:",
        reply_markup=cancel_kb(),
    )
    await callback.answer()


@router.message(StateFilter(SettingsStates.wait_remove_admin))
async def process_remove_admin(message: Message, state: FSMContext):
    if not is_owner(message.from_user.id):
        return
    try:
        uid = int(message.text.strip())
        global ADMIN_IDS
        if uid in ADMIN_IDS:
            ADMIN_IDS.remove(uid)
        await db.set_setting("admin_ids", ", ".join(str(a) for a in ADMIN_IDS))
        await send_log("Admin boshqaruvi", f"Admin olib tashlandi: {uid}", f"ID{message.from_user.id}")
        await message.answer(f"✅ Foydalanuvchi {uid} adminlikdan olib tashlandi!", reply_markup=back_to_admin_kb())
    except ValueError:
        await message.answer("❌ Noto'g'ri ID.", reply_markup=cancel_kb())
        return
    await state.clear()
