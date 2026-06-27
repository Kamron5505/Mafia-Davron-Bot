from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from config import OWNER_ID, BOT_TOKEN
from database.db import Database
from keyboards.admin_kb import admin_groups_kb, back_to_admin_kb, cancel_kb
from utils.logger import send_log

router = Router()
db = Database()


class GroupStates(StatesGroup):
    wait_block_id = State()
    wait_block_reason = State()
    wait_unblock_id = State()
    wait_group_info_id = State()
    wait_leave_group_id = State()


def is_owner(user_id: int) -> bool:
    return user_id == OWNER_ID


@router.callback_query(F.data == "admin:groups")
async def admin_groups_menu(callback: CallbackQuery):
    if not is_owner(callback.from_user.id):
        await callback.answer("❌ Ruxsat yo'q!", show_alert=True)
        return
    await callback.message.edit_text(
        "🏘 *GURUHLAR BOSHQARUVI*\n\nKerakli amalni tanlang:",
        reply_markup=admin_groups_kb(),
    )
    await callback.answer()


@router.callback_query(F.data == "admin_group:list")
async def group_list(callback: CallbackQuery):
    if not is_owner(callback.from_user.id):
        await callback.answer("❌ Ruxsat yo'q!", show_alert=True)
        return
    groups = await db.get_all_groups()
    if not groups:
        await callback.message.edit_text("❌ Bot hech qanday guruhga qo'shilmagan.", reply_markup=back_to_admin_kb())
        await callback.answer()
        return

    text = "📋 *Bot qo'shilgan guruhlar:*\n\n"
    for g in groups:
        blocked = "🔒" if await db.is_group_blocked(g["group_id"]) else "✅"
        title = g["title"] or "Noma'lum"
        text += f"{blocked} `{g['group_id']}` — {title} (👥 {g['members_count']})\n"
    await callback.message.edit_text(text, reply_markup=back_to_admin_kb())
    await callback.answer()


@router.callback_query(F.data == "admin_group:block")
async def block_group_prompt(callback: CallbackQuery, state: FSMContext):
    if not is_owner(callback.from_user.id):
        await callback.answer("❌ Ruxsat yo'q!", show_alert=True)
        return
    await state.set_state(GroupStates.wait_block_id)
    await callback.message.edit_text(
        "🔒 Bloklash uchun guruh ID sini yuboring:",
        reply_markup=cancel_kb(),
    )
    await callback.answer()


@router.message(StateFilter(GroupStates.wait_block_id))
async def process_block_group_id(message: Message, state: FSMContext):
    if not is_owner(message.from_user.id):
        return
    try:
        group_id = int(message.text.strip())
        await state.update_data(block_group_id=group_id)
        await state.set_state(GroupStates.wait_block_reason)
        await message.answer("📝 Bloklash sababini yozing (yoki \"-\" ni yuboring):", reply_markup=cancel_kb())
    except ValueError:
        await message.answer("❌ Noto'g'ri ID.", reply_markup=cancel_kb())
        await state.clear()


@router.message(StateFilter(GroupStates.wait_block_reason))
async def process_block_group_reason(message: Message, state: FSMContext):
    if not is_owner(message.from_user.id):
        return
    data = await state.get_data()
    group_id = data["block_group_id"]
    reason = message.text.strip() if message.text.strip() != "-" else ""
    await state.clear()

    await db.block_group(group_id, reason)
    reason_text = reason or "Ko'rsatilmagan"
    await send_log("Guruh bloklash", f"Guruh {group_id} bloklandi. Sabab: {reason_text}", f"ID{message.from_user.id}")
    await message.answer(
        f"✅ Guruh `{group_id}` bloklandi!\nSabab: {reason_text}",
        reply_markup=back_to_admin_kb(),
    )


@router.callback_query(F.data == "admin_group:unblock")
async def unblock_group_prompt(callback: CallbackQuery, state: FSMContext):
    if not is_owner(callback.from_user.id):
        await callback.answer("❌ Ruxsat yo'q!", show_alert=True)
        return
    await state.set_state(GroupStates.wait_unblock_id)
    await callback.message.edit_text(
        "🔓 Cheklovni olib tashlash uchun guruh ID sini yuboring:",
        reply_markup=cancel_kb(),
    )
    await callback.answer()


@router.message(StateFilter(GroupStates.wait_unblock_id))
async def process_unblock_group(message: Message, state: FSMContext):
    if not is_owner(message.from_user.id):
        return
    try:
        group_id = int(message.text.strip())
        await state.clear()
        await db.unblock_group(group_id)
        await send_log("Guruh unblock", f"Guruh {group_id} cheklovi olib tashlandi", f"ID{message.from_user.id}")
        await message.answer(f"✅ Guruh `{group_id}` cheklovi olib tashlandi!", reply_markup=back_to_admin_kb())
    except ValueError:
        await message.answer("❌ Noto'g'ri ID.", reply_markup=cancel_kb())
        await state.clear()


@router.callback_query(F.data == "admin_group:groupinfo")
async def group_info_prompt(callback: CallbackQuery, state: FSMContext):
    if not is_owner(callback.from_user.id):
        await callback.answer("❌ Ruxsat yo'q!", show_alert=True)
        return
    await state.set_state(GroupStates.wait_group_info_id)
    await callback.message.edit_text(
        "👤 Ma'lumot olish uchun guruh ID sini yuboring:",
        reply_markup=cancel_kb(),
    )
    await callback.answer()


@router.message(StateFilter(GroupStates.wait_group_info_id))
async def process_group_info(message: Message, state: FSMContext):
    if not is_owner(message.from_user.id):
        return
    try:
        group_id = int(message.text.strip())
        await state.clear()

        group_data = None
        all_groups = await db.get_all_groups()
        for g in all_groups:
            if g["group_id"] == group_id:
                group_data = g
                break

        if not group_data:
            await message.answer("❌ Guruh topilmadi.", reply_markup=back_to_admin_kb())
            return

        blocked = await db.is_group_blocked(group_id)
        status = "🔒 Bloklangan" if blocked else "Faol ✅"
        title = group_data["title"] or "Noma'lum"
        added = (group_data["added_at"] or "Noma'lum")[:10] if group_data["added_at"] else "Noma'lum"

        text = (
            f"🏘 *GURUH MA'LUMOTI*\n"
            f"🆔 ID: `{group_id}`\n"
            f"📛 Nomi: {title}\n"
            f"👥 A'zolar: {group_data['members_count']}\n"
            f"🎮 O'tkazilgan o'yinlar: {group_data['games_played']}\n"
            f"📅 Bot qo'shilgan: {added}\n"
            f"🔒 Holati: {status}"
        )
        await message.answer(text, reply_markup=back_to_admin_kb())
    except ValueError:
        await message.answer("❌ Noto'g'ri ID.", reply_markup=cancel_kb())
        await state.clear()


@router.callback_query(F.data == "admin_group:leave")
async def leave_group_prompt(callback: CallbackQuery, state: FSMContext):
    if not is_owner(callback.from_user.id):
        await callback.answer("❌ Ruxsat yo'q!", show_alert=True)
        return
    await state.set_state(GroupStates.wait_leave_group_id)
    await callback.message.edit_text(
        "🚪 Chiqish uchun guruh ID sini yuboring:",
        reply_markup=cancel_kb(),
    )
    await callback.answer()


@router.message(StateFilter(GroupStates.wait_leave_group_id))
async def process_leave_group(message: Message, state: FSMContext):
    if not is_owner(message.from_user.id):
        return
    try:
        group_id = int(message.text.strip())
        await state.clear()

        from aiogram import Bot
        bot = Bot(token=BOT_TOKEN)
        try:
            await bot.leave_chat(group_id)
            await db.remove_bot_group(group_id)
            await send_log("Guruhdan chiqish", f"Bot guruhdan chiqarildi: {group_id}", f"ID{message.from_user.id}")
            await message.answer(f"✅ Bot `{group_id}` guruhidan chiqarildi!", reply_markup=back_to_admin_kb())
        except Exception as e:
            await message.answer(f"❌ Xatolik: {e}", reply_markup=back_to_admin_kb())
        await bot.session.close()
    except ValueError:
        await message.answer("❌ Noto'g'ri ID.", reply_markup=cancel_kb())
        await state.clear()


@router.message(Command("grouplist"))
async def cmd_group_list(message: Message):
    if not is_owner(message.from_user.id):
        return
    groups = await db.get_all_groups()
    if not groups:
        await message.answer("❌ Bot hech qanday guruhga qo'shilmagan.")
        return
    text = "📋 *Bot qo'shilgan guruhlar:*\n\n"
    for g in groups:
        blocked = "🔒" if await db.is_group_blocked(g["group_id"]) else "✅"
        title = g["title"] or "Noma'lum"
        text += f"{blocked} `{g['group_id']}` — {title} (👥 {g['members_count']})\n"
    await message.answer(text)


@router.message(Command("blockgroup"))
async def cmd_block_group(message: Message):
    if not is_owner(message.from_user.id):
        return
    args = message.text.split(maxsplit=2)
    if len(args) < 2:
        await message.answer("❌ /blockgroup <group_id> [sabab]")
        return
    try:
        group_id = int(args[1])
        reason = args[2] if len(args) > 2 else ""
        await db.block_group(group_id, reason)
        await send_log("Guruh bloklash", f"Guruh {group_id} bloklandi. Sabab: {reason or '—'}", f"ID{message.from_user.id}")
        await message.answer(f"✅ Guruh `{group_id}` bloklandi!")
    except ValueError:
        await message.answer("❌ Noto'g'ri ID.")


@router.message(Command("unblockgroup"))
async def cmd_unblock_group(message: Message):
    if not is_owner(message.from_user.id):
        return
    args = message.text.split()
    if len(args) < 2:
        await message.answer("❌ /unblockgroup <group_id>")
        return
    try:
        group_id = int(args[1])
        await db.unblock_group(group_id)
        await send_log("Guruh unblock", f"Guruh {group_id} cheklovi olib tashlandi", f"ID{message.from_user.id}")
        await message.answer(f"✅ Guruh `{group_id}` cheklovi olib tashlandi!")
    except ValueError:
        await message.answer("❌ Noto'g'ri ID.")


@router.message(Command("groupinfo"))
async def cmd_group_info(message: Message):
    if not is_owner(message.from_user.id):
        return
    args = message.text.split()
    if len(args) < 2:
        await message.answer("❌ /groupinfo <group_id>")
        return
    try:
        group_id = int(args[1])
        all_groups = await db.get_all_groups()
        group_data = None
        for g in all_groups:
            if g["group_id"] == group_id:
                group_data = g
                break
        if not group_data:
            await message.answer("❌ Guruh topilmadi.")
            return
        blocked = await db.is_group_blocked(group_id)
        status = "🔒 Bloklangan" if blocked else "Faol ✅"
        title = group_data["title"] or "Noma'lum"
        added = (group_data["added_at"] or "Noma'lum")[:10] if group_data["added_at"] else "Noma'lum"
        text = (
            f"🏘 *GURUH MA'LUMOTI*\n"
            f"🆔 ID: `{group_id}`\n"
            f"📛 Nomi: {title}\n"
            f"👥 A'zolar: {group_data['members_count']}\n"
            f"🎮 O'tkazilgan o'yinlar: {group_data['games_played']}\n"
            f"📅 Bot qo'shilgan: {added}\n"
            f"🔒 Holati: {status}"
        )
        await message.answer(text)
    except ValueError:
        await message.answer("❌ Noto'g'ri ID.")


@router.message(Command("leavegroup"))
async def cmd_leave_group(message: Message):
    if not is_owner(message.from_user.id):
        return
    args = message.text.split()
    if len(args) < 2:
        await message.answer("❌ /leavegroup <group_id>")
        return
    try:
        group_id = int(args[1])
        from aiogram import Bot
        bot = Bot(token=BOT_TOKEN)
        try:
            await bot.leave_chat(group_id)
            await db.remove_bot_group(group_id)
            await send_log("Guruhdan chiqish", f"Bot guruhdan chiqarildi: {group_id}", f"ID{message.from_user.id}")
            await message.answer(f"✅ Bot `{group_id}` guruhidan chiqarildi!")
        except Exception as e:
            await message.answer(f"❌ Xatolik: {e}")
        await bot.session.close()
    except ValueError:
        await message.answer("❌ Noto'g'ri ID.")
