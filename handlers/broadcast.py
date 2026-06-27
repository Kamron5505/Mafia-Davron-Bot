import asyncio
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, ContentType
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.exceptions import TelegramAPIError
from config import OWNER_ID, BOT_TOKEN
from database.db import Database
from keyboards.admin_kb import back_to_admin_kb, cancel_kb, confirm_kb
from utils.logger import send_log

router = Router()
db = Database()


class BroadcastStates(StatesGroup):
    wait_message = State()
    wait_text_for_user = State()


def is_owner(user_id: int) -> bool:
    return user_id == OWNER_ID


@router.callback_query(F.data == "admin:broadcast")
async def broadcast_menu(callback: CallbackQuery):
    if not is_owner(callback.from_user.id):
        await callback.answer("❌ Ruxsat yo'q!", show_alert=True)
        return
    from keyboards.admin_kb import InlineKeyboardBuilder, InlineKeyboardButton
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(text="👤 Barcha foydalanuvchilarga", callback_data="broadcast:users"),
    )
    builder.row(
        InlineKeyboardButton(text="🏘 Barcha guruhlarga", callback_data="broadcast:groups"),
    )
    builder.row(
        InlineKeyboardButton(text="👤 Bitta foydalanuvchiga", callback_data="broadcast:user"),
    )
    builder.row(
        InlineKeyboardButton(text="🔙 Orqaga", callback_data="admin:back"),
    )
    await callback.message.edit_text(
        "📢 *XABAR YUBORISH (ELON)*\n\nQaysi turdagi xabarni yubormoqchisiz?",
        reply_markup=builder.as_markup(),
    )
    await callback.answer()


@router.callback_query(F.data == "broadcast:users")
async def broadcast_to_users(callback: CallbackQuery, state: FSMContext):
    if not is_owner(callback.from_user.id):
        await callback.answer("❌ Ruxsat yo'q!", show_alert=True)
        return
    await state.update_data(broadcast_type="users")
    await state.set_state(BroadcastStates.wait_message)
    await callback.message.edit_text(
        "📝 Yubormoqchi bo'lgan xabarni yuboring (matn, rasm, video, sticker, tugma):\n\n"
        "Xabar HTML formatida bo'lishi mumkin.\n"
        "Tugma qo'shish uchun format: `URL|Tugma matni` (xabarning eng oxirgi qatoriga yozing).",
        reply_markup=cancel_kb(),
    )
    await callback.answer()


@router.callback_query(F.data == "broadcast:groups")
async def broadcast_to_groups(callback: CallbackQuery, state: FSMContext):
    if not is_owner(callback.from_user.id):
        await callback.answer("❌ Ruxsat yo'q!", show_alert=True)
        return
    await state.update_data(broadcast_type="groups")
    await state.set_state(BroadcastStates.wait_message)
    await callback.message.edit_text(
        "📝 Guruhlarga yubormoqchi bo'lgan xabarni yuboring (matn, rasm, video):",
        reply_markup=cancel_kb(),
    )
    await callback.answer()


@router.callback_query(F.data == "broadcast:user")
async def broadcast_to_user(callback: CallbackQuery, state: FSMContext):
    if not is_owner(callback.from_user.id):
        await callback.answer("❌ Ruxsat yo'q!", show_alert=True)
        return
    await state.set_state(BroadcastStates.wait_text_for_user)
    await callback.message.edit_text(
        "👤 Foydalanuvchi ID sini yuboring:",
        reply_markup=cancel_kb(),
    )
    await callback.answer()


@router.message(StateFilter(BroadcastStates.wait_text_for_user))
async def process_broadcast_user_id(message: Message, state: FSMContext):
    if not is_owner(message.from_user.id):
        return
    try:
        user_id = int(message.text.strip())
        await state.update_data(target_user_id=user_id)
        await state.set_state(BroadcastStates.wait_message)
        await message.answer(
            "📝 Foydalanuvchiga yubormoqchi bo'lgan xabarni yuboring:",
            reply_markup=cancel_kb(),
        )
    except ValueError:
        await message.answer("❌ Noto'g'ri ID.", reply_markup=cancel_kb())
        await state.clear()


@router.message(StateFilter(BroadcastStates.wait_message))
async def process_broadcast_message(message: Message, state: FSMContext):
    if not is_owner(message.from_user.id):
        return
    data = await state.get_data()
    broadcast_type = data.get("broadcast_type", "users")

    await state.update_data(
        broadcast_message=message,
    )

    if broadcast_type == "users":
        total = await db.get_players_count()
    elif broadcast_type == "groups":
        total = len(await db.get_all_groups())
    else:
        total = 1

    await state.set_state(None)

    await message.answer(
        f"📢 *Tasdiqlash*\n\n"
        f"Tur: {broadcast_type}\n"
        f"Jami: {total} ta\n\n"
        f"Xabarni yuborishni tasdiqlaysizmi?",
        reply_markup=confirm_kb(f"send_broadcast:{broadcast_type}"),
    )


@router.callback_query(F.data.startswith("confirm:send_broadcast:"))
async def confirm_broadcast(callback: CallbackQuery, state: FSMContext):
    if not is_owner(callback.from_user.id):
        await callback.answer("❌ Ruxsat yo'q!", show_alert=True)
        return

    broadcast_type = callback.data.split(":")[2]
    data = await state.get_data()
    msg = data.get("broadcast_message")

    if not msg:
        await callback.message.edit_text("❌ Xabar topilmadi.", reply_markup=back_to_admin_kb())
        await callback.answer()
        await state.clear()
        return

    await state.clear()

    await callback.message.edit_text("⏳ Xabar yuborilmoqda...")
    await callback.answer()

    from aiogram import Bot
    bot = Bot(token=BOT_TOKEN)

    targets = []
    if broadcast_type == "users":
        players = await db.get_all_players()
        targets = [p["user_id"] for p in players]
    elif broadcast_type == "groups":
        groups = await db.get_all_groups()
        targets = [g["group_id"] for g in groups]
    elif broadcast_type == "user":
        target_user_id = data.get("target_user_id")
        if target_user_id:
            targets = [target_user_id]

    success = 0
    failed = 0

    progress_msg = await callback.message.edit_text(f"📤 Yuborildi: 0/{len(targets)}...")

    for i, target_id in enumerate(targets):
        try:
            await send_message_copy(bot, target_id, msg)
            success += 1
        except TelegramAPIError:
            failed += 1
        except Exception:
            failed += 1

        if (i + 1) % 10 == 0:
            try:
                await progress_msg.edit_text(f"📤 Yuborildi: {success}/{len(targets)}...")
            except Exception:
                pass

    await progress_msg.edit_text(
        f"✅ *Yuborish tugadi!*\n\n"
        f"✅ Muvaffaqiyatli: {success}\n"
        f"❌ Xato: {failed}",
        reply_markup=back_to_admin_kb(),
    )

    await send_log(
        "Broadcast",
        f"Tur: {broadcast_type}, Muvaffaqiyatli: {success}, Xato: {failed}",
        f"ID{callback.from_user.id}",
    )
    await bot.session.close()


async def send_message_copy(bot, chat_id: int, message: Message):
    if message.content_type == ContentType.TEXT:
        text = message.html_text or message.text
        reply_markup = None
        lines = text.split("\n")
        if lines and "|" in lines[-1] and lines[-1].startswith("http"):
            url_line = lines.pop()
            url, btn_text = url_line.split("|", 1)
            from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
            reply_markup = InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text=btn_text.strip(), url=url.strip())]
            ])
            text = "\n".join(lines)

        await bot.send_message(chat_id, text, reply_markup=reply_markup)

    elif message.content_type == ContentType.PHOTO:
        photo = message.photo[-1]
        caption = message.html_text or message.caption or ""
        await bot.send_photo(chat_id, photo.file_id, caption=caption)

    elif message.content_type == ContentType.VIDEO:
        video = message.video
        caption = message.html_text or message.caption or ""
        await bot.send_video(chat_id, video.file_id, caption=caption)

    elif message.content_type == ContentType.STICKER:
        await bot.send_sticker(chat_id, message.sticker.file_id)

    elif message.content_type == ContentType.ANIMATION:
        animation = message.animation
        caption = message.html_text or message.caption or ""
        await bot.send_animation(chat_id, animation.file_id, caption=caption)

    elif message.content_type == ContentType.DOCUMENT:
        doc = message.document
        caption = message.html_text or message.caption or ""
        await bot.send_document(chat_id, doc.file_id, caption=caption)

    elif message.content_type == ContentType.VOICE:
        await bot.send_voice(chat_id, message.voice.file_id)

    elif message.content_type == ContentType.VIDEO_NOTE:
        await bot.send_video_note(chat_id, message.video_note.file_id)

    else:
        await bot.send_message(chat_id, message.text or "Xabar")


@router.message(Command("broadcast"))
async def cmd_broadcast(message: Message):
    if not is_owner(message.from_user.id):
        return
    from keyboards.admin_kb import InlineKeyboardBuilder, InlineKeyboardButton
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(text="👤 Barcha foydalanuvchilarga", callback_data="broadcast:users"),
    )
    builder.row(
        InlineKeyboardButton(text="🏘 Barcha guruhlarga", callback_data="broadcast:groups"),
    )
    builder.row(
        InlineKeyboardButton(text="👤 Bitta foydalanuvchiga", callback_data="broadcast:user"),
    )
    await message.answer(
        "📢 *XABAR YUBORISH*\n\nQaysi turdagi xabarni yubormoqchisiz?",
        reply_markup=builder.as_markup(),
    )


@router.message(Command("broadcastgroup"))
async def cmd_broadcast_group(message: Message):
    if not is_owner(message.from_user.id):
        return
    data = {"broadcast_type": "groups"}
    await message.answer(
        "📝 Guruhlarga yubormoqchi bo'lgan xabarni yuboring:",
        reply_markup=cancel_kb(),
    )


@router.message(Command("broadcastuser"))
async def cmd_broadcast_user(message: Message):
    if not is_owner(message.from_user.id):
        return
    args = message.text.split(maxsplit=1)
    if len(args) < 2:
        await message.answer("❌ /broadcastuser <user_id>")
        return
    try:
        user_id = int(args[1])
        from aiogram import Bot
        bot = Bot(token=BOT_TOKEN)
        try:
            await bot.send_message(user_id, "Bu test xabar.")
            await message.answer(f"✅ Foydalanuvchi {user_id} ga xabar yuborildi!")
        except Exception as e:
            await message.answer(f"❌ Xatolik: {e}")
        await bot.session.close()
    except ValueError:
        await message.answer("❌ Noto'g'ri ID.")
