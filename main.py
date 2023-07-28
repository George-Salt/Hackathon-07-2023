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
