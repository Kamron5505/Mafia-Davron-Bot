from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, PreCheckoutQuery, LabeledPrice
from aiogram.filters import Command
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from config import BOT_TOKEN, STARS_PACKAGES, OWNER_ID
from database.db import Database
from utils.logger import send_log

router = Router()
db = Database()


def buy_kb() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    for pkg in STARS_PACKAGES:
        builder.row(
            InlineKeyboardButton(
                text=f"{pkg['name']} — {pkg['stars']}⭐ ({pkg['price']}⭐)",
                callback_data=f"buy_package:{pkg['stars']}:{pkg['price']}",
            )
        )
    builder.row(
        InlineKeyboardButton(text="🔙 Orqaga", callback_data="back_main"),
    )
    return builder.as_markup()


@router.message(Command("buy"))
async def cmd_buy(message: Message):
    text = "⭐ *Stars sotib olish*\n\nQuyidagi paketlardan birini tanlang:\n\n"
    for pkg in STARS_PACKAGES:
        text += f"• {pkg['name']} — {pkg['stars']}⭐ — {pkg['price']}⭐ Telegram Stars\n"
    await message.answer(text, reply_markup=buy_kb())


@router.callback_query(F.data.startswith("buy_package:"))
async def handle_buy_package(callback: CallbackQuery):
    parts = callback.data.split(":")
    stars_amount = int(parts[1])
    price_amount = int(parts[2])

    from aiogram import Bot
    bot = Bot(token=BOT_TOKEN)

    prices = [LabeledPrice(label=f"{stars_amount}⭐", amount=price_amount)]

    await bot.send_invoice(
        chat_id=callback.from_user.id,
        title=f"{stars_amount}⭐ Stars sotib olish",
        description=f"Mafia bot uchun {stars_amount}⭐ Stars",
        payload=f"stars_{stars_amount}_{price_amount}",
        provider_token="",
        currency="XTR",
        prices=prices,
    )
    await bot.session.close()
    await callback.answer()


@router.pre_checkout_query()
async def pre_checkout_handler(pre_checkout: PreCheckoutQuery):
    await pre_checkout.answer(ok=True)


@router.message(F.successful_payment)
async def successful_payment_handler(message: Message):
    user_id = message.from_user.id
    payment = message.successful_payment
    payload = payment.invoice_payload

    if not payload.startswith("stars_"):
        return

    parts = payload.split("_")
    stars_amount = int(parts[1])
    price_amount = int(parts[2])

    await db.add_stars(user_id, stars_amount)
    await db.add_stars_log(user_id, stars_amount, "purchase", f"Telegram Stars orqali sotib olingan")
    await db.add_payment(user_id, payment.telegram_payment_charge_id, stars_amount, price_amount)

    new_balance = await db.get_stars_balance(user_id)
    await message.answer(
        f"✅ *Sotib olish muvaffaqiyatli!*\n\n"
        f"⭐ {stars_amount} Stars hisobingizga qo'shildi!\n"
        f"💰 Yangi balans: {new_balance}⭐"
    )

    await send_log(
        "Stars sotib olish",
        f"Foydalanuvchi {user_id} {stars_amount}⭐ sotib oldi ({price_amount} Telegram Stars). Balans: {new_balance}⭐",
        "Avtomatik",
    )
