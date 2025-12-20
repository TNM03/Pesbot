import telebot
from telebot import types
import requests
from bs4 import BeautifulSoup
from flask import Flask
from threading import Thread

# BOT SOZLAMALARI
TOKEN = "8597572815:AAEOgOf8UCmRdoZtHqqkDl-D9Zt0oRRj2LY"
bot = telebot.TeleBot(TOKEN)
app = Flask('')

@app.route('/')
def home(): return "Bot Ishlamoqda!"

# Qidiruv funksiyasi
def search_player(name):
    query = f"{name} efootballhub player"
    url = f"https://www.bing.com/search?q={query.replace(' ', '+')}"
    headers = {'User-Agent': 'Mozilla/5.0'}
    try:
        res = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(res.text, 'html.parser')
        links = soup.find_all('a', href=True)
        results = []
        for link in links:
            href = link['href']
            if "efootballhub.net/efootball23/player/" in href:
                title = link.text.split('|')[0].strip()
                results.append({'name': title, 'url': href})
            if len(results) >= 3: break
        return results
    except: return []

@bot.message_handler(commands=['start'])
def start(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add("📊 Ehtimollikni hisoblash", "📈 Maksimal reyting")
    markup.add("📅 So'nggi yangiliklar")
    bot.send_message(message.chat.id, "Xush kelibsiz! Bo'limni tanlang:", reply_markup=markup)

@bot.message_handler(func=lambda m: True)
def handle_text(message):
    if message.text == "📈 Maksimal reyting":
        msg = bot.send_message(message.chat.id, "Futbolchi ismini kiriting (inglizcha):")
        bot.register_next_step_handler(msg, process_search)
    elif message.text == "📊 Ehtimollikni hisoblash":
        bot.send_message(message.chat.id, "Tangalar miqdorini kiriting:")
    elif message.text == "📅 So'nggi yangiliklar":
        bot.send_message(message.chat.id, "📌 Dushanba: Epic Box.\n📌 Payshanba: POTW.")

def process_search(message):
    wait = bot.send_message(message.chat.id, "🔎 Qidirilmoqda...")
    cards = search_player(message.text)
    bot.delete_message(message.chat.id, wait.message_id)
    if not cards:
        bot.send_message(message.chat.id, "❌ Hech narsa topilmadi.")
        return
    markup = types.InlineKeyboardMarkup()
    for c in cards:
        markup.add(types.InlineKeyboardButton(c['name'], url=c['url']))
    bot.send_message(message.chat.id, "Topilgan kartalar (Saytga o'tish uchun bosing):", reply_markup=markup)

def run(): app.run(host='0.0.0.0', port=8080)
if __name__ == "__main__":
    Thread(target=run).start()
    bot.polling(none_stop=True)
        
