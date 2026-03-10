# Version 1.2

import telebot
from telebot import types
import json
import os
import time
from config import TOKEN
from knowledge.medical_rules import (
    generate_status,
    generate_risks,
    generate_recommendations
)

bot = telebot.TeleBot(TOKEN)
DATA_FILE = "data/users.json"

user_states = {}
user_data = {}
def save_users(data):
    os.makedirs("data", exist_ok=True)
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

def load_users():
    if not os.path.exists(DATA_FILE):
        return {}
    with open(DATA_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

user_data = load_users()

def show_typing(chat_id, seconds=1.5):
    bot.send_chat_action(chat_id, "typing")
    time.sleep(seconds)

def main_menu(chat_id):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.row("📝 Профиль", "📊 Статус")
    markup.row("⚠️ Риски", "🧠 Рекомендации")
    bot.send_message(chat_id, "Выберите действие:", reply_markup=markup)

@bot.message_handler(commands=["start"])
def start(message):
    chat_id = message.chat.id
    user_states[chat_id] = "onboarding"

    bot.send_message(
        chat_id,
        "👋 *Добро пожаловать в HealthBot!*\n\n"
        "Я помогу оценить текущее состояние вашего здоровья и дам персональные рекомендации.\n\n"
        "⚠️ Все рекомендации носят информационный характер и не заменяют консультацию врача.",
        parse_mode="Markdown"
    )

    show_typing(chat_id)

    markup = types.InlineKeyboardMarkup()
    markup.add(
        types.InlineKeyboardButton("🚀 Начать опрос", callback_data="start_assessment"),
        types.InlineKeyboardButton("ℹ️ Как это работает", callback_data="about_bot")
    )
    bot.send_message(
        chat_id,
        "Перед началом задам несколько вопросов.\nЭто займёт около *2 минут*.",
        reply_markup=markup,
        parse_mode="Markdown"
    )

@bot.callback_query_handler(func=lambda call: True)
def callbacks(call):
    chat_id = call.message.chat.id
    bot.answer_callback_query(call.id)

    if call.data == "start_assessment":
        user_data[str(chat_id)] = {}
        ask_gender(chat_id)

    elif call.data == "about_bot":
        bot.send_message(
            chat_id,
            "ℹ️ *О боте*\n\n"
            "Я анализирую:\n"
            "• Индекс массы тела\n"
            "• Давление\n"
            "• Пульс\n"
            "• Сон\n"
            "• Физическую активность\n\n"
            "Все рекомендации носят информационный характер.",
            parse_mode="Markdown"
        )

def ask_gender(chat_id):
    user_states[str(chat_id)] = "sex"
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    markup.row("М", "Ж")
    bot.send_message(chat_id, "Выберите ваш пол:", reply_markup=markup)

def ask_age(chat_id):
    user_states[str(chat_id)] = "age"
    bot.send_message(chat_id, "Введите ваш возраст (полных лет):")

def ask_height(chat_id):
    user_states[str(chat_id)] = "height"
    bot.send_message(chat_id, "Введите ваш рост (см):")

def ask_weight(chat_id):
    user_states[str(chat_id)] = "weight"
    bot.send_message(chat_id, "Введите ваш вес (кг):")

def ask_pulse(chat_id):
    user_states[str(chat_id)] = "pulse"
    bot.send_message(chat_id, "Введите пульс в покое (уд/мин):")

def ask_pressure(chat_id):
    user_states[str(chat_id)] = "pressure"
    bot.send_message(chat_id, "Введите давление (пример: 120/80):")

def ask_sleep(chat_id):
    user_states[str(chat_id)] = "sleep"
    bot.send_message(chat_id, "Сколько часов вы спите в сутки?")

def ask_activity(chat_id):
    user_states[str(chat_id)] = "activity"
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    markup.row("низкий", "средний", "высокий")
    bot.send_message(chat_id, "Выберите уровень физической активности:", reply_markup=markup)

@bot.message_handler(func=lambda m: str(m.chat.id) in user_states)
def handle_profile(message):
    chat_id = str(message.chat.id)
    state = user_states[chat_id]
    text = message.text.strip()

    try:
        if state == "sex":
            if text not in ["М", "Ж"]:
                bot.send_message(chat_id, "Пожалуйста, выберите пол кнопкой.")
                return
            user_data[chat_id]["sex"] = text
            ask_age(chat_id)

        elif state == "age":
            if not text.isdigit() or not (1 <= int(text) <= 120):
                bot.send_message(chat_id, "Введите корректный возраст.")
                return
            user_data[chat_id]["age"] = int(text)
            ask_height(chat_id)

        elif state == "height":
            if not text.isdigit() or not (100 <= int(text) <= 250):
                bot.send_message(chat_id, "Введите корректный рост.")
                return
            user_data[chat_id]["height"] = int(text)
            ask_weight(chat_id)

        elif state == "weight":
            weight = float(text)
            if not (30 <= weight <= 250):
                raise ValueError
            user_data[chat_id]["weight"] = weight
            ask_pressure(chat_id)

        elif state == "pressure":
            if "/" not in text:
                bot.send_message(chat_id, "Введите давление в формате 120/80.")
                return
            sys, dia = text.split("/")
            if not (sys.isdigit() and dia.isdigit()):
                bot.send_message(chat_id, "Введите корректное давление.")
                return
            user_data[chat_id]["pressure"] = [int(sys), int(dia)]
            ask_pulse(chat_id)

        elif state == "pulse":
            if not text.isdigit() or not (40 <= int(text) <= 200):
                bot.send_message(chat_id, "Введите корректный пульс.")
                return
            user_data[chat_id]["pulse"] = int(text)
            ask_sleep(chat_id)

        elif state == "sleep":
            sleep = float(text)
            if not (0 <= sleep <= 24):
                raise ValueError
            user_data[chat_id]["sleep"] = sleep
            ask_activity(chat_id)

        elif state == "activity":
            if text not in ["низкий", "средний", "высокий"]:
                bot.send_message(chat_id, "Выберите вариант кнопкой.")
                return
            user_data[chat_id]["activity"] = text

            del user_states[chat_id]
            save_users(user_data)

            bot.send_message(chat_id, "✅ Профиль успешно заполнен!")
            main_menu(chat_id)

    except Exception:
        bot.send_message(chat_id, "⚠️ Некорректный ввод. Попробуйте ещё раз.")

@bot.message_handler(func=lambda m: True)
def handle_menu(message):
    chat_id = str(message.chat.id)
    text = message.text

    if chat_id in user_states:
        return

    if chat_id not in user_data and text != "🚀 Начать":
        bot.send_message(chat_id, "Сначала заполните профиль.")
        return

    if text == "📝 Профиль":
        ask_gender(chat_id)

    elif text == "📊 Статус":
        bot.send_message(chat_id, generate_status(user_data[chat_id]))

    elif text == "⚠️ Риски":
        bot.send_message(chat_id, generate_risks(user_data[chat_id]))

    elif text == "🧠 Рекомендации":
        bot.send_message(chat_id, generate_recommendations(user_data[chat_id]))

    else:
        bot.send_message(chat_id, "Используйте кнопки меню 👇")

bot.polling(none_stop=True)
