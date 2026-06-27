from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder


def admin_panel_kb() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(text="👤 Foydalanuvchilar", callback_data="admin:users"),
        InlineKeyboardButton(text="🏘 Guruhlar", callback_data="admin:groups"),
    )
    builder.row(
        InlineKeyboardButton(text="⭐ Stars boshqaruvi", callback_data="admin:stars"),
        width=1,
    )
    builder.row(
        InlineKeyboardButton(text="📢 Xabar yuborish (Elon)", callback_data="admin:broadcast"),
        width=1,
    )
    builder.row(
        InlineKeyboardButton(text="📊 Statistika", callback_data="admin:stats"),
        InlineKeyboardButton(text="⚙️ Sozlamalar", callback_data="admin:settings"),
    )
    builder.row(
        InlineKeyboardButton(text="🔙 Asosiy menyu", callback_data="back_main"),
    )
    return builder.as_markup()


def admin_users_kb() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(text="🚫 Ban", callback_data="admin_user:ban"),
        InlineKeyboardButton(text="🔓 Unban", callback_data="admin_user:unban"),
    )
    builder.row(
        InlineKeyboardButton(text="⭐ Add Stars", callback_data="admin_user:addstars"),
        InlineKeyboardButton(text="➖ Remove Stars", callback_data="admin_user:removestars"),
    )
    builder.row(
        InlineKeyboardButton(text="👤 User Info", callback_data="admin_user:userinfo"),
        InlineKeyboardButton(text="🔄 Reset Stats", callback_data="admin_user:resetstats"),
    )
    builder.row(
        InlineKeyboardButton(text="🚫 All Ban", callback_data="admin_user:allban"),
    )
    builder.row(
        InlineKeyboardButton(text="🔙 Orqaga", callback_data="admin:back"),
    )
    return builder.as_markup()


def admin_groups_kb() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(text="📋 Guruhlar ro'yxati", callback_data="admin_group:list"),
    )
    builder.row(
        InlineKeyboardButton(text="🔒 Block guruh", callback_data="admin_group:block"),
        InlineKeyboardButton(text="🔓 Unblock", callback_data="admin_group:unblock"),
    )
    builder.row(
        InlineKeyboardButton(text="👤 Group Info", callback_data="admin_group:groupinfo"),
        InlineKeyboardButton(text="🚪 Chiqish", callback_data="admin_group:leave"),
    )
    builder.row(
        InlineKeyboardButton(text="🔙 Orqaga", callback_data="admin:back"),
    )
    return builder.as_markup()


def admin_stars_kb() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(text="⭐ Add Stars", callback_data="admin_stars:add"),
        InlineKeyboardButton(text="➖ Remove Stars", callback_data="admin_stars:remove"),
    )
    builder.row(
        InlineKeyboardButton(text="📜 Stars Log", callback_data="admin_stars:log"),
        InlineKeyboardButton(text="💳 Pending Payments", callback_data="admin_stars:pending"),
    )
    builder.row(
        InlineKeyboardButton(text="📊 Umumiy statistika", callback_data="admin_stars:total"),
    )
    builder.row(
        InlineKeyboardButton(text="🔙 Orqaga", callback_data="admin:back"),
    )
    return builder.as_markup()


def admin_settings_kb() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(text="📢 Log kanal", callback_data="admin_set:logchannel"),
    )
    builder.row(
        InlineKeyboardButton(text="👥 Min o'yinchilar", callback_data="admin_set:minplayers"),
        InlineKeyboardButton(text="👥 Max o'yinchilar", callback_data="admin_set:maxplayers"),
    )
    builder.row(
        InlineKeyboardButton(text="🔧 Maintenance", callback_data="admin_set:maintenance"),
    )
    builder.row(
        InlineKeyboardButton(text="👑 Admin qo'shish", callback_data="admin_set:addadmin"),
        InlineKeyboardButton(text="👑 Admin olib tashlash", callback_data="admin_set:removeadmin"),
    )
    builder.row(
        InlineKeyboardButton(text="🔙 Orqaga", callback_data="admin:back"),
    )
    return builder.as_markup()


def admin_stats_kb() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(text="🔄 Yangilash", callback_data="admin_stats:refresh"),
    )
    builder.row(
        InlineKeyboardButton(text="🔙 Orqaga", callback_data="admin:back"),
    )
    return builder.as_markup()


def confirm_kb(callback_data: str) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(text="✅ Tasdiqlash", callback_data=f"confirm:{callback_data}"),
        InlineKeyboardButton(text="❌ Bekor qilish", callback_data=f"confirm:cancel"),
    )
    return builder.as_markup()


def back_to_admin_kb() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(text="🔙 Admin panel", callback_data="admin:back"),
    )
    return builder.as_markup()


def cancel_kb() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(text="❌ Bekor qilish", callback_data="admin:cancel"),
    )
    return builder.as_markup()
