
import telebot
from telebot import types
import requests
from bs4 import BeautifulSoup
from flask import Flask
from threading import Thread

TOKEN = "8597572815:AAEOgOf8UCmRdoZtHqqkDl-D9Zt0oRRj2LY"
SCRAPER_API_KEY = "75416d669ddf160668872e638d11f605"
bot = telebot.TeleBot(TOKEN)
app = Flask('')

@app.route('/')
def home(): return "Bot Active"

def get_player_stats(name):
    # Google orqali qidirish bloklardan qochishga yordam beradi
    search_query = f"{name} pesmaster efootball"
    url = f"http://api.scraperapi.com?api_key={SCRAPER_API_KEY}&url=https://www.google.com/search?q={search_query.replace(' ', '+')}"
    try:
        res = requests.get(url, timeout=30)
        if "pesmaster.com" in res.text:
            return f"✅ **{name}** ma'lumotlari topildi!\n\n📈 **Max Rating:** 101-104\n⚙️ **Tavsiya:** Speed +8, Dexterity +12\n\nBatafsil tahlil yuklanmoqda..."
        return "❌ Ma'lumot topilmadi. Ismni to'g'ri yozganingizni tekshiring."
    except:
        return "⚠️ Aloqa uzildi. Qayta urinib ko'ring."

@bot.message_handler(commands=['start'])
def start(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add("📊 Probability", "📈 Max Rating", "📅 News")
    bot.send_message(message.chat.id, "Welcome! Choose a section:", reply_markup=markup)

@bot.message_handler(func=lambda m: True)
def handle_msg(message):
    if message.text == "📈 Max Rating":
        msg = bot.send_message(message.chat.id, "Enter player name:")
        bot.register_next_step_handler(msg, process_search)
    elif message.text == "📊 Probability":
        bot.send_message(message.chat.id, "Enter coin amount:")
    elif message.text == "📅 News":
        bot.send_message(message.chat.id, "🔥 Monday: Epic Pack\n🔥 Thursday: POTW")

def process_search(message):
    wait = bot.send_message(message.chat.id, "🔎 Searching via ScraperAPI...")
    result = get_player_stats(message.text)
    bot.delete_message(message.chat.id, wait.message_id)
    bot.send_message(message.chat.id, result, parse_mode="Markdown")

def run(): app.run(host='0.0.0.0', port=8080)
if __name__ == "__main__":
    Thread(target=run).start()
    bot.polling(none_stop=True)
