from telegram_bot.utils import StatesUsers

# СООБЩЕНИЯ ОТ БОТА
first_start_message = 'Приветствуем вас на пректе "Копилка" Для начала вступите в наш телеграмм канал где вы сможете ознакомить с презентацией проекта'
stat_message = 'Приветствуем вас на пректе "Копилка"'
start_admin_message = "Приветствую админ 👋"
not_command_message = "Такой команды нет"
not_in_group_message = "Для общения с этим ботом подпишись на канал!"
in_group_message = "Отлично!\n\n спасибо за подписку, давай начнём!"
sms_not_in_group_message = "Ты ещё не подписался на канал 🥺"
username_admin_message = "Для связ с поддержкой\nпиши сюда 👇"
add_admin_message = """ID состоит только из чисел, его можно получить тут https://t.me/getmyid_bot
Вводи ID пользователя:"""
not_admin_id_message = """Это не число, ID состоит только из чисел, его можно получить тут https://t.me/getmyid_bot
Вводи ID пользователя:"""
not_num_message = "Это не число!\nПопоробуй ещё раз"
not_balance_message = "На вашем балансе нет столько средств"
score_users_message = "Введите ваш номер счёта из Юmoney:"
not_score_users_message = "Это не похоже на номер счёта в Юmoney\nПопробуй ещё раз:"


MESSAGES = {
    "first_start": first_start_message,
    "start": stat_message,
    "start_admin": start_admin_message,
    "not_command": not_command_message,
    "not_in_group": not_in_group_message,
    "in_group": in_group_message,
    "sms_not_in_group": sms_not_in_group_message,
    "username_admin": username_admin_message,
    "add_admin": add_admin_message,
    "not_admin_id": not_admin_id_message,
    # "how_many_out": how_many_out_message,
    # "not_out": not_out_message,
    "not_num": not_num_message,
    "not_balance": not_balance_message,
    "score_users": score_users_message,
    "not_score_users": not_score_users_message,
}
