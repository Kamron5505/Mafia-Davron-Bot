import html
from aiogram import Router, F
from aiogram.enums import ParseMode
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from database.db import Database
from roles.base_role import get_all_roles, get_role
from utils.messages import SHOP_TEXT

router = Router()
db = Database()


def get_purchasable_roles() -> list:
    return [r for r in get_all_roles() if r.stars_cost > 0]


def shop_kb(user_id: int, purchased: list = None, team: str = None) -> InlineKeyboardMarkup:
    if purchased is None:
        purchased = []
    builder = InlineKeyboardBuilder()
    builder.max_width = 2

    roles = get_purchasable_roles()
    if team:
        roles = [r for r in roles if r.team == team]

    for role in roles:
        name = role.title
        price = role.stars_cost
        if role.name in purchased:
            name = f"✅ {name}"
        builder.row(
            InlineKeyboardButton(
                text=f"{role.emoji} {name} — {price}⭐",
                callback_data=f"shop_buy:{role.name}",
            )
        )

    # Team filter buttons (only if showing all)
    if not team:
        builder.row(
            InlineKeyboardButton(text="🦈 Mafiya", callback_data="shop_team:mafia"),
            InlineKeyboardButton(text="🛡 Shahar", callback_data="shop_team:town"),
            InlineKeyboardButton(text="🌪 Neytral", callback_data="shop_team:neutral"),
        )
    else:
        builder.row(
            InlineKeyboardButton(text="🔙 Barcha rollar", callback_data="shop_menu"),
        )

    builder.row(
        InlineKeyboardButton(text="🔙 Asosiy menyu", callback_data="back_main"),
    )
    return builder.as_markup()


async def has_purchased_role(user_id: int, role_name: str) -> bool:
    return role_name in await db.get_purchased_role_names(user_id)


@router.message(Command("shop"))
async def cmd_shop(message: Message):
    balance = await db.get_stars_balance(message.from_user.id)
    purchased = await db.get_purchased_role_names(message.from_user.id)
    text = SHOP_TEXT.format(balance=balance)
    if len(text) > 4000:
        text = text[:4000]
    await message.answer(text, reply_markup=shop_kb(message.from_user.id, purchased), parse_mode=ParseMode.HTML)


@router.callback_query(F.data == "shop_menu")
async def shop_menu(callback: CallbackQuery):
    balance = await db.get_stars_balance(callback.from_user.id)
    purchased = await db.get_purchased_role_names(callback.from_user.id)
    text = SHOP_TEXT.format(balance=balance)
    if len(text) > 4000:
        text = text[:4000]
    await callback.message.edit_text(text, reply_markup=shop_kb(callback.from_user.id, purchased), parse_mode=ParseMode.HTML)
    await callback.answer()


@router.callback_query(F.data.startswith("shop_team:"))
async def shop_by_team(callback: CallbackQuery):
    team = callback.data.split(":")[1]
    balance = await db.get_stars_balance(callback.from_user.id)
    purchased = await db.get_purchased_role_names(callback.from_user.id)

    team_labels = {"mafia": "🦈 Qora Kuchlar", "town": "🛡 Oq Kuchlar", "neutral": "🌪 Neytral Kuchlar"}
    team_text = team_labels.get(team, team)
    text = f"⭐ <b>{team_text} roli</b>\n💰 Sizda: {balance}⭐\n———————————————\n"

    if len(text) > 4000:
        text = text[:4000]
    await callback.message.edit_text(text, reply_markup=shop_kb(callback.from_user.id, purchased, team), parse_mode=ParseMode.HTML)
    await callback.answer()


@router.callback_query(F.data.startswith("shop_buy:"))
async def handle_buy_role(callback: CallbackQuery):
    role_name = callback.data.split(":")[1]
    user_id = callback.from_user.id

    role = get_role(role_name)
    if not role:
        await callback.answer("❌ Rol topilmadi!", show_alert=True)
        return

    if role.stars_cost <= 0:
        await callback.answer("❌ Bu rolni sotib olish mumkin emas!", show_alert=True)
        return

    if await has_purchased_role(user_id, role_name):
        await callback.answer("❌ Siz bu rolni allaqachon sotib olgansiz!", show_alert=True)
        return

    balance = await db.get_stars_balance(user_id)
    if balance < role.stars_cost:
        await callback.answer(
            f"❌ Yetarli Stars yo'q! Kerak: {role.stars_cost}⭐, Sizda: {balance}⭐",
            show_alert=True,
        )
        return

    text = (
        f"{role.emoji} <b>{html.escape(role.title)}</b> rolini {role.stars_cost}⭐ ga sotib olishni "
        f"xohlaysizmi?\n\n"
        f"📖 {html.escape(role.description)}\n"
        f"🏷 Tim: {html.escape(role.team_label())}\n\n"
        f"💰 Sizda: {balance}⭐\n"
        f"💸 Narx: {role.stars_cost}⭐"
    )
    await callback.message.edit_text(
        text,
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="✅ Ha, sotib olish", callback_data=f"shop_confirm:{role.name}")],
            [InlineKeyboardButton(text="❌ Bekor qilish", callback_data="shop_menu")],
        ]),
        parse_mode=ParseMode.HTML,
    )
    await callback.answer()


@router.callback_query(F.data.startswith("shop_confirm:"))
async def handle_confirm_buy(callback: CallbackQuery):
    role_name = callback.data.split(":")[1]
    user_id = callback.from_user.id

    role = get_role(role_name)
    if not role:
        await callback.answer("❌ Rol topilmadi!", show_alert=True)
        await callback.message.edit_text("❌ Xatolik yuz berdi.", reply_markup=InlineKeyboardMarkup(
            inline_keyboard=[[InlineKeyboardButton(text="🔙 Orqaga", callback_data="shop_menu")]]
        ))
        return

    if await has_purchased_role(user_id, role_name):
        await callback.answer("❌ Siz bu rolni allaqachon sotib olgansiz!", show_alert=True)
        return

    balance = await db.get_stars_balance(user_id)
    if balance < role.stars_cost:
        await callback.answer("❌ Yetarli Stars yo'q!", show_alert=True)
        return

    await db.remove_stars(user_id, role.stars_cost)
    await db.buy_role(user_id, role_name)
    await db.add_stars_log(user_id, -role.stars_cost, "role_purchase",
                           f"Sotib olindi: {role.title} ({role.name})")

    new_balance = await db.get_stars_balance(user_id)
    await callback.message.edit_text(
        f"✅ <b>Rol muvaffaqiyatli sotib olindi!</b>\n\n"
        f"{role.emoji} <b>{html.escape(role.title)}</b>\n"
        f"📖 {html.escape(role.description)}\n"
        f"🏷 Tim: {html.escape(role.team_label())}\n\n"
        f"💰 Yangi balans: {new_balance}⭐\n\n"
        f"🎮 Bu rol keyingi o'yinlarda sizga beriladi!",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="🛒 Do'konga qaytish", callback_data="shop_menu")],
            [InlineKeyboardButton(text="🔙 Asosiy menyu", callback_data="back_main")],
        ]),
        parse_mode=ParseMode.HTML,
    )
    await callback.answer("✅ Rol sotib olindi!", show_alert=True)
