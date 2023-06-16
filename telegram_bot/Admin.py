import os
from openpyxl import Workbook
from aiogram.types import Message
from aiogram.dispatcher import FSMContext, Dispatcher

from telegram_bot.utils import StatesAdmin
from telegram_bot.KeyboardButton import BUTTON_TYPES
from content_text.messages import MESSAGES
from cfg.config import ADMIN_ID, BANNED_ID, MIN_OUT, MIN_PAY
from cfg.database import Database
from create_bot import dp, bot

db = Database('cfg/database')


# ===================================================
# ===================== АДМИНКА =====================
# ===================================================
# =============== ДОБАВИТЬ АДМИНА ===============
async def add_admin(message: Message):
    if message.from_user.id in ADMIN_ID:
        await message.answer(MESSAGES["add_admin"], reply_markup=BUTTON_TYPES["BTN_CANCEL"])
        state = dp.current_state(user=message.from_user.id)
        await state.set_state(StatesAdmin.all()[1])

    else:
        await message.answer(MESSAGES['start'], reply_markup=BUTTON_TYPES["BTN_HOME"])


# =============== ВВОД ID АДМИНА ===============
async def id_admin(message: Message, state: FSMContext):
    if message.text.lower() == "отмена":
        await message.answer(MESSAGES['start_admin'], reply_markup=BUTTON_TYPES["BTN_HOME_ADMIN"])
        await state.finish()
    elif message.text.isnumeric():
        new_users_id = int(message.text)
        ADMIN_ID.append(new_users_id)
        await message.answer("Добавил!", reply_markup=BUTTON_TYPES["BTN_HOME_ADMIN"])
        await state.finish()
    else:
        await message.answer(MESSAGES["not_admin_id"], reply_markup=BUTTON_TYPES["BTN_CANCEL"])
        await state.set_state(StatesAdmin.all()[1])


# ===============================================================
# =============== ВЫВОД ПОЛЬЗОВАТЕЛЕЙ/РЕФЕРАЛОВ =================
# ===============================================================
async def views_users(message: Message):
    if message.from_user.id in ADMIN_ID:
        write_to_excel_all_users(db.get_all_data(), "все_пользователи.xlsx")
        with open("все_пользователи.xlsx", 'rb') as file:
            await bot.send_document(message.from_user.id, file)
        await message.answer(MESSAGES["start"], reply_markup=BUTTON_TYPES["BTN_HOME_ADMIN"])
        os.remove("все_пользователи.xlsx")
    else:
        await bot.send_message(message.from_user.id, MESSAGES["not_command"], reply_markup=BUTTON_TYPES["BTN_HOME"])


def write_to_excel_all_users(data, filename):
    workbook = Workbook()
    sheet = workbook.active
    headers = ["id", "user_id", "username", "кто пригласил", "Бан", "Баланс в копейках", "Когда первый раз пополнил счёт", "Сколько сегодня снимут"]
    sheet.append(headers)
    for row in data:
        sheet.append(row)
    workbook.save(filename)


# ===============================================================
# ===================== ДАТЬ/УБРАТЬ БАН =========================
# ===============================================================
async def add_ban(message: Message):
    if message.from_user.id in ADMIN_ID:
        if message.text.lower() == "дать бан":
            await message.answer('Впиш id пользователя для бана:', reply_markup=BUTTON_TYPES["BTN_CANCEL"])
        else:
            await message.answer('Впиш id пользователя для того, что бы снять бан:', reply_markup=BUTTON_TYPES["BTN_CANCEL"])

        state = dp.current_state(user=message.from_user.id)
        await state.update_data(what_d=message.text)
        await state.set_state(StatesAdmin.all()[2])
    else:
        await bot.send_message(message.from_user.id, MESSAGES["not_command"], reply_markup=BUTTON_TYPES["BTN_HOME"])


# ===================== ДАТЬ/УБРАТЬ БАН =========================
async def check_ban(message: Message, state: FSMContext):
    try:
        all_data = await state.get_data()

        if message.text.lower() == "отмена":
            await message.answer(MESSAGES['start'], reply_markup=BUTTON_TYPES["BTN_HOME_ADMIN"])
            await state.finish()

        elif all_data["what_d"] == "Дать бан":
            BANNED_ID.append(int(message.text))
            await message.answer('Пользователю выдан бан', reply_markup=BUTTON_TYPES["BTN_HOME_ADMIN"])
        else:
            try:
                BANNED_ID.remove(int(message.text))
                await message.answer('Пользователю убран бан', reply_markup=BUTTON_TYPES["BTN_HOME_ADMIN"])
            except:
                await message.answer('Этот пользователь не в бане', reply_markup=BUTTON_TYPES["BTN_HOME_ADMIN"])

        await state.finish()
    except:
        await message.answer('id состоит только из цифр\nПопробуй ввести ещё раз:', reply_markup=BUTTON_TYPES["BTN_CANCEL"])
        await state.set_state(StatesAdmin.all()[2])


# =======================================================================================
# ===================== ИЗМЕНИТЬ МИНИМАЛЬНОЕ ПОПОЛНЕНИЕ БАЛАНСА =========================
# =======================================================================================
async def min_out_balance(message: Message):
    if message.from_user.id in ADMIN_ID:
        if message.text.lower() == "MIN пополнение":
            await message.answer('Впиш число для минимального пополнения баланса:', reply_markup=BUTTON_TYPES["BTN_CANCEL"])
        else:
            await message.answer('Впиш число для минимального вывода средств:', reply_markup=BUTTON_TYPES["BTN_CANCEL"])

        state = dp.current_state(user=message.from_user.id)
        await state.update_data(what_balance=message.text)
        await state.set_state(StatesAdmin.all()[3])
    else:
        await bot.send_message(message.from_user.id, MESSAGES["not_command"], reply_markup=BUTTON_TYPES["BTN_HOME"])


# ===================== ИЗМЕНИТЬ МИНИМАЛЬНОЕ ПОПОЛНЕНИЕ БАЛАНСА =========================
async def check_min_balance(message: Message, state: FSMContext):
    try:
        all_data = await state.get_data()

        if message.text.lower() == "отмена":
            await message.answer(MESSAGES['start'], reply_markup=BUTTON_TYPES["BTN_HOME_ADMIN"])
            await state.finish()

        elif all_data["what_balance"] == "MIN пополнение":
            MIN_PAY[0] = int(message.text)
            await message.answer('Изменено!', reply_markup=BUTTON_TYPES["BTN_HOME_ADMIN"])
        else:
            MIN_OUT[0] = int(message.text)
            await message.answer('Изменено!', reply_markup=BUTTON_TYPES["BTN_HOME_ADMIN"])

        await state.finish()
    except:
        await message.answer('id состоит только из цифр\nПопробуй ввести ещё раз:', reply_markup=BUTTON_TYPES["BTN_CANCEL"])
        await state.set_state(StatesAdmin.all()[3])


def register_handler_admin(dp: Dispatcher):
    dp.register_message_handler(add_admin, lambda message: message.text.lower() == 'добавить админа')
    dp.register_message_handler(id_admin, state=StatesAdmin.STATES_1)
    dp.register_message_handler(views_users, lambda message: message.text.lower() == 'статистика')

    # ДАТЬ/УБРАТЬ БАН
    dp.register_message_handler(add_ban, lambda message: message.text.lower() == 'дать бан' or message.text.lower() == 'убрать бан')
    dp.register_message_handler(check_ban, state=StatesAdmin.STATES_2)

    # ИЗМЕНИТЬ МИНИМАЛЬНЫЙ БАЛАНС
    dp.register_message_handler(min_out_balance, lambda message: message.text.lower() == 'min пополнение' or message.text.lower() == 'min вывод')
    dp.register_message_handler(check_min_balance, state=StatesAdmin.STATES_3)