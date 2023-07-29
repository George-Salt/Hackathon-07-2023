import json
import os

import telebot
from dotenv import load_dotenv
load_dotenv()


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
    register_button = telebot.types.KeyboardButton("Зарегистрироваться (для сотрудника)")
    admin_button = telebot.types.KeyboardButton("Админка (для компании)")

    markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add(login_button, register_button, admin_button)

    BOT.send_message(
        message.chat.id,
        "Добро пожаловать в меню сотрудников компании Company!\n\nВыберите действие, исползуя кнопки.",
        reply_markup=markup
    )


if __name__ == "__main__":
    BOT.infinity_polling()
