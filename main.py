import telebot
from telebot import types
import requests
from bs4 import BeautifulSoup
from flask import Flask
from threading import Thread
import os

# MUHIM: Tokeningizni quyidagi qo'shtirnoq ichiga aniq yozing
TOKEN = "8597572815:AAEOgOf8UCmRdoZtHqqkDl-D9Zt0oRRj2LY"
bot = telebot.TeleBot(TOKEN)
app = Flask('')

@app.route('/')
def home():
    return "Bot ishlamoqda!"

def get_player_list(player_name):
    search_url = f"https://www.efootballdb.com/search?name={player_name.replace(' ', '+')}"
    headers = {'User-Agent': 'Mozilla/5.0'}
    try:
        response = requests.get(search_url, headers=headers, timeout=10)
        soup = BeautifulSoup(response.text, 'html.parser')
        players = soup.find_all('a', class_='player-name', limit=5)
        return [{"name": p.text.strip(), "link": "https://www.efootballdb.com" + p['href']} for p in players]
    except:
        return []

@bot.message_handler(commands=['start'])
def start(message):
    bot.reply_to(message, "Assalomu alaykum! Futbolchi ismini inglizcha yozing (masalan: Messi):")

@bot.message_handler(func=lambda message: True)
def handle_search(message):
    name = message.text
    bot.send_message(message.chat.id, f"🔎 '{name}' tahlil qilinmoqda...")
    players = get_player_list(name)
    if players:
        markup = types.InlineKeyboardMarkup()
        for p in players:
            markup.add(types.InlineKeyboardButton(text=f"🃏 {p['name']}", url=p['link']))
        bot.send_message(message.chat.id, "Topilgan kartalar:", reply_markup=markup)
    else:
        bot.send_message(message.chat.id, "❌ Topilmadi.")

def run():
    app.run(host='0.0.0.0', port=8080)

if __name__ == "__main__":
    t = Thread(target=run)
    t.start()
    try:
        bot.polling(none_stop=True)
    except Exception as e:
        print(f"Xatolik yuz berdi: {e}")
