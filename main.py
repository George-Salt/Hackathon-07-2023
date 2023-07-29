import json
import os

import requests
import telebot
from dotenv import load_dotenv

load_dotenv()


ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD")
TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
BOT = telebot.TeleBot(TOKEN)


def get_data(filepath="users.json"):
    with open(filepath, "r", encoding="utf-8") as file:
        data = json.load(file)
    return data


def save_data(data, filepath="users.json"):
    with open(filepath, "w", encoding="utf-8") as file:
        json.dump(data, file)


@BOT.message_handler(commands=["start"])
def start(message):
    login_button = telebot.types.KeyboardButton("Войти (для сотрудника)")
    register_button = telebot.types.KeyboardButton(
        "Зарегистрироваться (для сотрудника)"
    )
    admin_button = telebot.types.KeyboardButton("Админка (для компании)")

    markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add(login_button, register_button, admin_button)

    menu_message = BOT.send_message(
        message.chat.id,
        """\
        Добро пожаловать в меню сотрудников компании Company!
        \nВыберите действие, используя кнопки.""",
        reply_markup=markup
    )
    BOT.register_next_step_handler(menu_message, define_menu_command)


def define_menu_command(message):
    command = message.text
    back_button = telebot.types.KeyboardButton("Вернуться")

    back_markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
    back_markup.add(back_button)

    if command == "Войти (для сотрудника)":
        message = BOT.send_message(
            message.chat.id,
            "Введите ваш логин.",
            reply_markup=back_markup
        )
        BOT.register_next_step_handler(
            message,
            get_username_to_login,
            back_markup
        )
    elif command == "Зарегистрироваться (для сотрудника)":
        message = BOT.send_message(
            message.chat.id,
            "Придумайте логин.",
            reply_markup=back_markup
        )
        BOT.register_next_step_handler(
            message,
            get_username_to_register,
            back_markup
        )
    elif command == "Админка (для компании)":
        message = BOT.send_message(
            message.chat.id,
            "Введите пароль от администрации.",
            reply_markup=back_markup
        )
        BOT.register_next_step_handler(
            message,
            get_password_to_admin,
            back_markup
        )


def get_password_to_admin(message, markup):
    if message.text == "Вернуться":
        start(message)
    else:
        if message.text == ADMIN_PASSWORD:
            users_info_to_message = ["Информация о пользователях"]
            for user in users:
                username = user["username"]
                password = user["password"]
                name = user["name"]
                age = user["age"]
                user_info = f"Пользователь {name} - имя пользователя: {username}, пароль: {password}, возраст: {age}."
                users_info_to_message.append(user_info)
                
            users_info_message = "\n".join(users_info_to_message)
        
            BOT.send_message(
                message.chat.id,
                users_info_message,
                reply_markup=markup
            )
            start(message)


def get_username_to_login(message, markup):
    if message.text == "Вернуться":
        start(message)
    else:
        is_exist = False
        for user in users:
            if user["username"] == message.text:
                is_exist = True

        if is_exist:
            message = BOT.send_message(message.chat.id, "Введите ваш пароль.", reply_markup=markup)
            BOT.register_next_step_handler(
                message,
                get_password_to_login,
                user
            )
        else:
            BOT.send_message(message.chat.id, "Такого логина не существует!")
            start(message)


def get_password_to_login(message, user):
    if message.text == "Вернуться":
        start(message)
    else:
        if user["password"] == message.text:
            username = user["username"]
            BOT.send_message(message.chat.id, f"Вы вошли как {username}.")
            send_user_commands(message, user)
        else:
            BOT.send_message(
                message.chat.id,
                "Неверный пароль! Повторите попытку."
            )
            BOT.register_next_step_handler(
                message,
                get_password_to_login,
                user
            )


def get_username_to_register(message, markup):
    if message.text == "Вернуться":
        start(message)
    else:
        is_repeat = False
        for user in users:
            if user["username"] == message.text:
                is_repeat = True

        if is_repeat:
            message = BOT.send_message(
                message.chat.id,
                "Такое имя пользователя уже занято! Повторите попытку.",
                reply_markup=markup
            )
            BOT.register_next_step_handler(
                message,
                get_username_to_register,
                markup
            )
        else:
            user = {"username": message.text, "password": "", "name": "без имени", "age": "не указано"}

            message = BOT.send_message(
                message.chat.id,
                "Придумайте пароль.",
                reply_markup=markup
            )
            BOT.register_next_step_handler(
                message,
                get_password_to_register, 
                user
            )


def get_password_to_register(message, user):
    if message.text == "Вернуться":
        start(message)
    else:
        if len(message.text) >= 4:
            user["password"] = message.text
            users.append(user)
            save_data(users)

            username = user["username"]
            BOT.send_message(message.chat.id, f"Вы вошли как {username}.")
            send_user_commands(message, user)
        else:
            BOT.send_message(
                message.chat.id,
                "Слишком короткий пароль! Повторите попытку."
            )
            BOT.register_next_step_handler(
                message,
                get_password_to_register,
                user
            )


def send_user_commands(message, user):
    change_name_button = telebot.types.KeyboardButton("Добавить/сменить имя")
    change_age_button = telebot.types.KeyboardButton(
        "Добавить/изменить возраст"
    )
    change_password_button = telebot.types.KeyboardButton("Сменить пароль")
    delete_account_button = telebot.types.KeyboardButton(
        "Удалить учетную запись"
    )
    quit_button = telebot.types.KeyboardButton("Выйти")

    markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add(
        change_name_button,
        change_age_button,
        change_password_button,
        delete_account_button,
        quit_button
    )

    for index, finding_user in enumerate(users):
        if finding_user["username"] == user["username"]:
            name = user["name"]
            age = user["age"]
            username = user["username"]
            password = user["password"]
            users[index] = user
    save_data(users)

    profile = f"""\
    Профиль
    \nИмя: {name}.
    \nВозраст: {age}.
    \nЛогин: {username}.
    \nПароль: {password}.
    \nВыберите действие, используя кнопки."""
    message = BOT.send_message(message.chat.id, profile, reply_markup=markup)
    BOT.register_next_step_handler(
        message,
        define_user_command,
        user
    )


def define_user_command(message, user):
    command = message.text
    if command == "Добавить/сменить имя":
        message = BOT.send_message(message.chat.id, "Введите новое имя.")
        BOT.register_next_step_handler(
            message,
            change_name,
            user
        )
    elif command == "Добавить/изменить возраст":
        message = BOT.send_message(message.chat.id, "Введите ваш возраст.")
        BOT.register_next_step_handler(
            message,
            change_age,
            user
        )
    elif command == "Сменить пароль":
        message = BOT.send_message(message.chat.id, "Введите новый пароль.")
        BOT.register_next_step_handler(
            message,
            change_password,
            user
        )
    elif command == "Добавить/изменить возраст":
        delete_account(message, user)
    elif command == "Выйти":
        start(message)


def change_name(message, user):
    for index, finding_user in enumerate(users):
        if finding_user["username"] == user["username"]:
            user["name"] = message.text
            users[index] = user
    save_data(users)
    BOT.send_message(message.chat.id, f"Имя изменено на {message.text}.")
    send_user_commands(message, user)


def change_age(message, user):
    for index, finding_user in enumerate(users):
        if finding_user["username"] == user["username"]:
            user["age"] = message.text
            users[index] = user
    save_data(users)
    BOT.send_message(message.chat.id, f"Возраст изменен на {message.text}.")
    send_user_commands(message, user)


def change_password(message, user):
    if len(message.text) >= 4:
        user["password"] = message.text
        for index, finding_user in enumerate(users):
            if finding_user["username"] == user["username"]:
                user["password"] = message.text
                users[index] = user
        save_data(users)

        BOT.send_message(message.chat.id, f"Пароль изменен на {message.text}.")
        send_user_commands(message, user)
    else:
        BOT.send_message(
            message.chat.id,
            "Слишком короткий пароль! Повторите попытку."
        )
        BOT.register_next_step_handler(
            message,
            get_password_to_register,
            user
        )


def delete_account(message, user):
    users.remove(user)
    save_data(users)
    BOT.send_message(message.chat.id, "Пользователь успешно удален!")
    start(message)


if __name__ == "__main__":
    global users
    users = get_data()
    while True:
        try:
            BOT.infinity_polling()
        except requests.exceptions.ConnectionError:
            continue
        except requests.exceptions.ReadTimeout:
            continue
    
