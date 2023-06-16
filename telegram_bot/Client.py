import datetime

from aiogram.types import Message, CallbackQuery, ContentType, InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.dispatcher import FSMContext, Dispatcher

from telegram_bot.utils import StatesUsers
from telegram_bot.KeyboardButton import BUTTON_TYPES
from content_text.messages import MESSAGES
from cfg.config import ADMIN_ID, ID_CHANNEL, BOT_NIK, TOKEN_YOOKASSA, MIN_PAY, MIN_OUT
from cfg.database import Database
from create_bot import dp, bot
from dop_functional.pay_out import generate_request

from yoomoney import Quickpay, Client

db = Database('cfg/database')


# ===================================================
# =============== СТАНДАРТНЫЕ КОМАНДЫ ===============
# ===================================================
async def start_command(message: Message):
    #   РЕФ СИСТЕМА
    if not db.user_exists(message.from_user.id):
        referer_id = str(message.text[7:])
        if referer_id != "":
            if referer_id != message.from_user.id:
                db.add_user(message.from_user.id, message.from_user.username, referer_id)
                try:
                    await bot.send_message(chat_id=referer_id, text="По вашей реферальной ссылке зарегестрировался новый пользователь!")
                except:
                    pass
        else:
            db.add_user(message.from_user.id, message.from_user.username)

    #   ПРОВЕРКА ПОДПИСКИ НА КАНАЛ
    user_channel_status = await bot.get_chat_member(chat_id=ID_CHANNEL, user_id=message.from_user.id)
    if user_channel_status["status"] != 'left':
        if message.from_user.id in ADMIN_ID:
            await message.answer(MESSAGES['start_admin'], reply_markup=BUTTON_TYPES["BTN_HOME_ADMIN"])

        else:
            await message.answer(MESSAGES['start'], reply_markup=BUTTON_TYPES["BTN_HOME"])

    else:
        await message.answer(MESSAGES['first_start'])
        await bot.send_message(message.from_user.id, MESSAGES["not_in_group"], reply_markup=BUTTON_TYPES["BTN_SUB"])
        state = dp.current_state(user=message.from_user.id)
        await state.set_state(StatesUsers.all()[0])


# ======================================================
# =============== 💵 Пополнить счёт 💵 =================
# ======================================================
async def replenish_balance(message: Message):
    await message.answer(f"Введи любую сумму для пополнения баланса (от {MIN_PAY[0]}руб)", reply_markup=BUTTON_TYPES["BTN_CANCEL"])
    state = dp.current_state(user=message.from_user.id)
    await state.set_state(StatesUsers.all()[1])


# =============== 💵 ПРОВЕРКА ВВЕДЁНОЙ СУММЫ 💵 =================
async def check_replenish_balance(message: Message, state: FSMContext):
    try:
        if message.text.lower() == "отмена":
            await message.answer(MESSAGES['start'], reply_markup=BUTTON_TYPES["BTN_HOME"])
            await state.finish()
        elif int(message.text) >= MIN_PAY[0]:
            id_pay = f"{message.from_user.id}_{message.message_id}"
            url_pay = str(payment(id_pay, message.text))
            await state.update_data(id_pay=id_pay)
            await state.update_data(url_pay=url_pay)
            await state.update_data(replenishment=f"{message.text}")

            btn_pay_yoomoney = InlineKeyboardButton(text="Оплатить", url=url_pay)
            btn_check_pay = InlineKeyboardButton(text="Проверить оплату", callback_data="CHECK_PAY")
            btn_pay_cancel = InlineKeyboardButton(text="Отмена", callback_data="CANCEL")
            btn_pay1 = InlineKeyboardMarkup().add(btn_pay_yoomoney).add(btn_check_pay).add(btn_pay_cancel)

            await message.answer(f"💳 Ваш счёт на оплату {message.text}руб:", reply_markup=btn_pay1, parse_mode="HTML")
            await state.set_state(StatesUsers.all()[2])

        else:
            await message.answer(f"Это число меньше {MIN_PAY[0]}руб", reply_markup=BUTTON_TYPES["BTN_CANCEL"])
            await state.set_state(StatesUsers.all()[1])
    except:
        await message.answer(f"Это число меньше {MIN_PAY[0]}руб", reply_markup=BUTTON_TYPES["BTN_CANCEL"])
        await state.set_state(StatesUsers.all()[1])


# =============== 💵 ПРОВЕРКА ОПЛАТЫ 💵 =================
async def check_pay(callback: CallbackQuery, state: FSMContext):
    if callback.data == "CHECK_PAY":
        client = Client(TOKEN_YOOKASSA)
        id_pay = await state.get_data()
        history = client.operation_history(label=id_pay["id_pay"])

        btn_pay_url = InlineKeyboardButton(text="Оплатить", url=id_pay["url_pay"])
        btn_check_pay = InlineKeyboardButton(text="Проверить ещё раз", callback_data="CHECK_PAY")
        btn_pay_cancel = InlineKeyboardButton(text="Отмена", callback_data="CANCEL")
        btn_pay_again = InlineKeyboardMarkup().add(btn_pay_url).add(btn_check_pay).add(btn_pay_cancel)

        if not history.operations:
            await callback.message.edit_reply_markup()

            await callback.message.answer("Оплата не прошла!!!", reply_markup=btn_pay_again)
            await state.set_state(StatesUsers.all()[2])
        else:
            my_b = db.get_balance(callback.from_user.id)

            if my_b[1] is None:
                date_now_reg = datetime.datetime.now().strftime("%Y-%m-%d")
                db.register_day(callback.from_user.id, date_now_reg, 1)

            new_balance = await state.get_data()
            new_balance = int(new_balance["replenishment"]) * 100

            db.add_balance(callback.from_user.id, new_balance)
            await callback.message.edit_reply_markup()
            await bot.send_message(callback.from_user.id, "Баланс пополнен", reply_markup=BUTTON_TYPES["BTN_HOME"])
            await state.finish()

    elif callback.data == "CANCEL":
        await callback.message.edit_reply_markup()
        await callback.message.answer(MESSAGES['start'], reply_markup=BUTTON_TYPES["BTN_HOME"])
        await state.finish()


# ФОРМИРОВАНИЕ ССЫЛКИ ДЛЯ ОПЛАТЫ
def payment(id_pay, value_yookassa):
    quickpay = Quickpay(
            receiver="4100116335995110",
            quickpay_form="shop",
            targets='Оплата',
            paymentType="SB",
            sum=value_yookassa,
            label=id_pay
            )

    return quickpay.base_url


# ======================================================
# =============== 💸 Вывод средств 💸 ==================
# ======================================================
async def out_balance(message: Message):
    print(MIN_PAY)
    print(MIN_OUT)
    info_balance = db.get_balance(message.from_user.id)
    try:
        how_many_days = datetime.datetime.now().date() - datetime.datetime.strptime(info_balance[2], "%Y-%m-%d").date()
        if int(how_many_days.days) <= 10:
            await message.answer(f"{message.from_user.first_name}, вывод средств не доступен!"
                                 f"\nВыод доступен спустя 10дней после первого пополнения"
                                 f"\nВам осталось ждать: {10 - int(how_many_days.days)}", reply_markup=BUTTON_TYPES["BTN_HOME"])

        elif int(how_many_days.days) > 10:
            await message.answer(f"Введите сумму для вывода средств(от {MIN_OUT[0]}руб):", reply_markup=BUTTON_TYPES["BTN_CANCEL"])
            state = dp.current_state(user=message.from_user.id)
            await state.set_state(StatesUsers.all()[3])
        else:
            await message.answer(f"{message.from_user.first_name}, вам пока не доступен вывод средств!\nОн будет доступен после первого пополнения баланса", reply_markup=BUTTON_TYPES["BTN_HOME"])

    except Exception as ex:
        print(ex)
        await message.answer(f"{message.from_user.first_name}, вам пока не доступен вывод средств!\nОн будет доступен после первого пополнения баланса", reply_markup=BUTTON_TYPES["BTN_HOME"])


# =============== 💸 ПРОВЕРКА 💸 ==================
async def check_input_out(message: Message, state: FSMContext):
    info_balance = db.get_balance(message.from_user.id)[0] / 100

    try:
        if MIN_OUT[0] <= int(message.text) <= info_balance:
            await state.update_data(sum_out=f"{message.text}")
            await message.answer(MESSAGES["score_users"], reply_markup=BUTTON_TYPES["BTN_CANCEL"])
            await state.set_state(StatesUsers.all()[4])

        elif int(message.text) < MIN_OUT[0]:
            await message.answer(f"Это число меньше {MIN_OUT[0]}руб", reply_markup=BUTTON_TYPES["BTN_CANCEL"])
            await state.set_state(StatesUsers.all()[3])

        elif int(message.text) > info_balance:
            await message.answer(MESSAGES["not_balance"], reply_markup=BUTTON_TYPES["BTN_CANCEL"])
            await state.set_state(StatesUsers.all()[3])

        else:
            await message.answer(MESSAGES["not_num"], reply_markup=BUTTON_TYPES["BTN_CANCEL"])
            await state.set_state(StatesUsers.all()[3])

    except:
        if message.text.lower() == "отмена":
            await message.answer(MESSAGES['start'], reply_markup=BUTTON_TYPES["BTN_HOME"])
            await state.finish()
        else:
            await message.answer(MESSAGES["not_num"], reply_markup=BUTTON_TYPES["BTN_CANCEL"])
            await state.set_state(StatesUsers.all()[3])


# =============== 💸 ПРОВЕРКА 💸 ==================
async def get_score(message: Message, state: FSMContext):
    if message.text.lower() == "отмена":
        await message.answer(MESSAGES['start'], reply_markup=BUTTON_TYPES["BTN_HOME"])
        await state.finish()

    elif message.text.isdigit() and len(message.text) == 16:
        try:
            amount_get = await state.get_data()
            message_text = generate_request(amount_get["sum_out"], message.text)

            if message_text == 'Перевод успешно подтвержден':
                out_m = int(amount_get["sum_out"]) * 100
                db.out_money(message.from_user.id, out_m)

            await message.answer(message_text, reply_markup=BUTTON_TYPES["BTN_HOME"])
            await state.finish()

        except:
            await message.answer("Произошла ошибка(\nПопробуйте снова", reply_markup=BUTTON_TYPES["BTN_HOME"])
            await state.finish()

    else:
        await message.answer(MESSAGES["not_score_users"], reply_markup=BUTTON_TYPES["BTN_CANCEL"])
        await state.set_state(StatesUsers.all()[4])


# ================================================
# =============== 💰 Баланс 💰 ===================
# ================================================
async def my_balance(message: Message):
    my_b = db.get_balance(message.from_user.id)
    if my_b is None:
        await message.answer(f"Ваш баланс: 0руб", reply_markup=BUTTON_TYPES["BTN_HOME"])
    else:
        await message.answer(f"Ваш баланс: {my_b[0] / 100}руб\nБлижайшее списание сегодня в 24:00 по МСК\nСегодня спишут: {my_b[1]}руб", reply_markup=BUTTON_TYPES["BTN_HOME"])


# =============================================================
# =============== 👨‍👨‍👦‍👦 Реферальная система 👨‍👨‍👦‍👦 =================
# =============================================================
async def ref_system(message: Message):
    try:
        await message.answer(
            f"Твой ID: {message.from_user.id}\nТвоя реферальная ссылка: https://t.me/{BOT_NIK}?start={message.from_user.id}"
            f"\nКол-во рефералов: {db.count_referer(message.from_user.id)}", reply_markup=BUTTON_TYPES["BTN_HOME"])
    except:
        pass


# ===================================================
# =============== 🤖  ПОДДЕРЖКА 🤖 =================
# ===================================================
async def contact_admin(message: Message):
    await message.answer(MESSAGES["username_admin"], reply_markup=BUTTON_TYPES["ADMIN_URL"])


# =================================================
# =============== ПРОВЕРКА ПОДПИСКИ ===============
# =================================================
async def check_sub(message: Message):
    state = dp.current_state(user=message.from_user.id)
    user_channel_status = await bot.get_chat_member(chat_id=ID_CHANNEL, user_id=message.from_user.id)
    if user_channel_status["status"] != 'left':
        await message.answer(MESSAGES['in_group'], reply_markup=BUTTON_TYPES["BTN_HOME"])
        state = dp.current_state(user=message.from_user.id)
        await state.finish()

    else:
        await bot.send_message(message.from_user.id, MESSAGES["not_in_group"], reply_markup=BUTTON_TYPES["BTN_SUB"])
        await state.set_state(StatesUsers.all()[0])


async def check_sub_q(callback: CallbackQuery):
    user_channel_status = await bot.get_chat_member(chat_id=ID_CHANNEL, user_id=callback.from_user.id)
    if user_channel_status["status"] != 'left':
        await callback.message.delete()
        await callback.message.answer(MESSAGES['in_group'], reply_markup=BUTTON_TYPES["BTN_HOME"])
        state = dp.current_state(user=callback.from_user.id)
        await state.finish()

    else:
        await callback.answer(MESSAGES["sms_not_in_group"], show_alert=True)


# ===================================================
# =============== ОТМЕНА ===============
# ===================================================
async def cansel_pay(message: Message, state: FSMContext):
    if message.from_user.id in ADMIN_ID:
        await message.answer(MESSAGES['start_admin'], reply_markup=BUTTON_TYPES["BTN_HOME_ADMIN"])
    else:
        await bot.send_message(message.from_user.id, MESSAGES["start"], reply_markup=BUTTON_TYPES["BTN_HOME"])
    await state.finish()


# ===================================================
# =============== НЕИЗВЕСТНАЯ КОМАНДА ===============
# ===================================================
async def unknown_command(message: Message):
    if message.from_user.id in ADMIN_ID:
        await message.answer(MESSAGES['not_command'], reply_markup=BUTTON_TYPES["BTN_HOME_ADMIN"])
    else:
        await bot.send_message(message.from_user.id, MESSAGES["not_command"], reply_markup=BUTTON_TYPES["BTN_HOME"])


def register_handler_client(dp: Dispatcher):
    dp.register_message_handler(start_command, commands="start")
    dp.register_message_handler(ref_system, lambda message: message.text == '👨‍👨‍👦‍👦 Реферальная система 👨‍👨‍👦‍👦')
    dp.register_message_handler(contact_admin, lambda message: message.text == '🤖 Поддержка 🤖')
    dp.register_message_handler(my_balance, lambda message: message.text == '💰 Баланс 💰')
    dp.register_message_handler(check_sub, state=StatesUsers.STATE_0)
    dp.register_callback_query_handler(check_sub_q, lambda callback: callback.data == "check", state=StatesUsers.STATE_0)

    dp.register_message_handler(replenish_balance, lambda message: message.text == '💵 Пополнить счёт 💵')
    dp.register_message_handler(check_replenish_balance, state=StatesUsers.STATE_1)
    dp.register_callback_query_handler(check_pay, state=StatesUsers.STATE_2)
    dp.register_message_handler(cansel_pay, lambda message: message.text == 'Отмена', state=StatesUsers.STATE_2)

    dp.register_message_handler(out_balance, lambda message: message.text == '💸 Вывод средств 💸')
    dp.register_message_handler(check_input_out, state=StatesUsers.STATE_3)
    dp.register_message_handler(get_score, state=StatesUsers.STATE_4)

    dp.register_message_handler(unknown_command, content_types=["text"])
