from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, KeyboardButton, ReplyKeyboardMarkup
from cfg.config import URL_CHANNEL

# =============================================
# ============= ДЛЯ ПОЛЬЗОВАТЕЛЕЙ =============
# =============================================
# КНОПКИ МЕНЮ
btn_conclusion = KeyboardButton("💸 Вывод средств 💸")
btn_replenish = KeyboardButton("💵 Пополнить счёт 💵")
btn_profile = KeyboardButton("💰 Баланс 💰")
btn_admin = KeyboardButton("🤖 Поддержка 🤖")
btn_part = KeyboardButton("👨‍👨‍👦‍👦 Реферальная система 👨‍👨‍👦‍👦")


btn_cancel = KeyboardButton("Отмена")

btn_sub_channel = InlineKeyboardButton(text="Подписаться", url=URL_CHANNEL)
btn_check_sub = InlineKeyboardButton(text="Проверить", callback_data="check")
btn_admin_url = InlineKeyboardButton(text="🤖 Поддержка 🤖", url="https://t.me/dribo1")


# =============================================
# ================ ДЛЯ АДМИНА =================
# =============================================
btn_stat = KeyboardButton("Статистика")
btn_ban = KeyboardButton("Дать бан")
btn_on_ban = KeyboardButton("Убрать бан")
btn_min_balance = KeyboardButton("MIN пополнение")
btn_min_out_balance = KeyboardButton("MIN вывод")
btn_add_admin = KeyboardButton("Добавить админа")


BUTTON_TYPES = {
    "BTN_HOME": ReplyKeyboardMarkup(resize_keyboard=True).add(btn_conclusion, btn_replenish).add(btn_profile).add(btn_admin, btn_part),

    "BTN_HOME_ADMIN": ReplyKeyboardMarkup(resize_keyboard=True).add(btn_stat).add(btn_ban, btn_on_ban).add(btn_min_balance, btn_min_out_balance).add(btn_add_admin),

    "BTN_CANCEL": ReplyKeyboardMarkup(resize_keyboard=True).add(btn_cancel),
    "BTN_SUB": InlineKeyboardMarkup().add(btn_sub_channel).add(btn_check_sub),
    "ADMIN_URL": InlineKeyboardMarkup().add(btn_admin_url),

}
