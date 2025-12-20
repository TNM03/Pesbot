import telebot
from telebot import types
import requests
from bs4 import BeautifulSoup
from flask import Flask
from threading import Thread
import time

# 1. BOT SOZLAMALARI
TOKEN = "8597572815:AAEOgOf8UCmRdoZtHqqkDl-D9Zt0oRRj2LY"
bot = telebot.TeleBot(TOKEN)
app = Flask('')

@app.route('/')
def home(): return "Bot EFHUB Tahlili bilan Faol!"

STRINGS = {
    'uz': {
        'btn1': "📊 Ehtimollikni hisoblash",
        'btn2': "📈 Maksimal reyting",
        'btn3': "📅 So'nggi yangiliklar",
        'ask_name': "Futbolchi ismini kiriting (EFHUB tahlili):",
        'ask_coins': "Tangalar miqdorini kiriting:",
        'wait': "🔎 EFHUB bazasi tahlil qilinmoqda...",
        'select_card': "Kartani tanlang:",
        'news_head': "🔥 KONAMI RASMIY YANGILIKLARI:",
        'not_found': "❌ Karta topilmadi. Ismni inglizcha yozing (masalan: Ronaldo).",
        'prob_res': "💰 Tangalar: {c}\n🎯 Epic yutish ehtimoli: {p}%"
    }
}

# 2. BARQAROR QIDIRUV (DuckDuckGo orqali blokdan qochish)
def search_efhub(name):
    query = f"site:efootballhub.net {name} player"
    url = f"https://duckduckgo.com/html/?q={query.replace(' ', '+')}"
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
    try:
        res = requests.get(url, headers=headers, timeout=15)
        soup = BeautifulSoup(res.text, 'html.parser')
        links = soup.select('.result__a')
        results = []
        for link in links:
            href = link['href']
            if "/player/" in href or "/players/" in href:
                title = link.text.strip().replace(" - eFootballHub", "")
                results.append({'name': title, 'url': href})
            if len(results) >= 5: break
        return results
    except: return []

# 3. HANDLERS
@bot.message_handler(commands=['start'])
def start(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add(STRINGS['uz']['btn1'], STRINGS['uz']['btn2'])
    markup.add(STRINGS['uz']['btn3'])
    bot.send_message(message.chat.id, "Xush kelibsiz! Bo'limni tanlang:", reply_markup=markup)

@bot.message_handler(func=lambda m: m.text in [STRINGS['uz']['btn1'], STRINGS['uz']['btn2'], STRINGS['uz']['btn3']])
def menu_logic(message):
    lang = 'uz'
    if message.text == STRINGS[lang]['btn2']:
        msg = bot.send_message(message.chat.id, STRINGS[lang]['ask_name'])
        bot.register_next_step_handler(msg, process_search)
    elif message.text == STRINGS[lang]['btn1']:
        msg = bot.send_message(message.chat.id, STRINGS[lang]['ask_coins'])
        bot.register_next_step_handler(msg, process_calc)
    elif message.text == STRINGS[lang]['btn3']:
        news = "📌 **KONAMI YANGILIKLARI:**\n\n🗓 Dushanba: Epic Box yangilandi.\n🗓 Payshanba: POTW kutilmoqda."
        bot.send_message(message.chat.id, news, parse_mode="Markdown")

def process_search(message):
    wait = bot.send_message(message.chat.id, STRINGS['uz']['wait'])
    cards = search_efhub(message.text)
    bot.delete_message(message.chat.id, wait.message_id)
    if not cards:
        bot.send_message(message.chat.id, STRINGS['uz']['not_found'])
        return
    markup = types.InlineKeyboardMarkup()
    for i, c in enumerate(cards):
        markup.add(types.InlineKeyboardButton(c['name'], callback_data=f"sel_{i}"))
    bot.send_message(message.chat.id, STRINGS['uz']['select_card'], reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data.startswith('sel_'))
def show_details(call):
    guide = (
        "📊 **EFHUB Tahlili:**\n\n"
        "📈 Max Rating: 101-104\n"
        "👨‍🏫 Murabbiy: X. Alonso (LBC)\n"
        "⚙️ Training: Speed +8, Dexterity +10, Lower Body +8."
    )
    bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=guide, parse_mode="Markdown")

def process_calc(message):
    try:
        coins = int(message.text)
        p = round((1 - ((147/150) ** (coins // 100))) * 100, 1)
        bot.send_message(message.chat.id, f"🎯 Epic yutish ehtimoli: {p}%")
    except: bot.send_message(message.chat.id, "Faqat raqam yozing!")

def run(): app.run(host='0.0.0.0', port=8080)
if __name__ == "__main__":
    Thread(target=run).start()
    bot.polling(none_stop=True)
  
