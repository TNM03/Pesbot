import telebot
from telebot import types
import requests
from bs4 import BeautifulSoup
from flask import Flask
from threading import Thread
import time

# 1. BOT SOZLAMALARI
TOKEN = "8597572815:AAEOgOf8UCmRdoZtHqqkDl-D9Zt0oRRj2LY" # O'z tokeningizni to'liq yozing
bot = telebot.TeleBot(TOKEN)
app = Flask('')

@app.route('/')
def home():
    return "Bot 3 tilda faol!"

# Tillar lug'ati
STRINGS = {
    'uz': {
        'welcome': "Xush kelibsiz! Tilni tanlang:",
        'ask_name': "Futbolchi ismini inglizcha yozing (masalan: Messi):",
        'searching': "🔎 '{name}' tahlil qilinmoqda...",
        'not_found': "❌ Afsuski, hech qanday karta topilmadi.",
        'found': "✅ '{name}' uchun topilgan kartalar:",
        'guide': "Karta haqida ma'lumot va Training Guide uchun tanlang:"
    },
    'ru': {
        'welcome': "Добро пожаловать! Выберите язык:",
        'ask_name': "Введите имя игрока на английском (например: Messi):",
        'searching': "🔎 Анализируем '{name}'...",
        'not_found': "❌ Карты не найдены.",
        'found': "✅ Найденные карты для '{name}':",
        'guide': "Выберите карту для просмотра Training Guide:"
    },
    'en': {
        'welcome': "Welcome! Choose your language:",
        'ask_name': "Enter player name in English (e.g., Messi):",
        'searching': "🔎 Analyzing '{name}'...",
        'not_found': "❌ No cards found.",
        'found': "✅ Found cards for '{name}':",
        'guide': "Select a card to view Training Guide:"
    }
}

user_lang = {} # Foydalanuvchi tilini saqlash

# 2. QIDIRUV FUNKSIYASI
def get_player_list(player_name):
    search_url = f"https://www.efootballdb.com/search?name={player_name.replace(' ', '+')}"
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
    try:
        response = requests.get(search_url, headers=headers, timeout=15)
        soup = BeautifulSoup(response.text, 'html.parser')
        players = soup.select('a[href*="/players/"]')
        results = []
        seen = set()
        for p in players:
            name = p.text.strip()
            link = "https://www.efootballdb.com" + p['href']
            if name and len(name) > 2 and link not in seen:
                results.append({"name": name, "link": link})
                seen.add(link)
            if len(results) >= 6: break
        return results
    except:
        return []

# 3. BOT LOGIKASI
@bot.message_handler(commands=['start'])
def start(message):
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("🇺🇿 O'zbekcha", callback_data='lang_uz'),
               types.InlineKeyboardButton("🇷🇺 Русский", callback_data='lang_ru'),
               types.InlineKeyboardButton("🇬🇧 English", callback_data='lang_en'))
    bot.send_message(message.chat.id, "Tilni tanlang / Выберите язык / Choose language:", reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data.startswith('lang_'))
def set_lang(call):
    lang = call.data.split('_')[1]
    user_lang[call.message.chat.id] = lang
    bot.answer_callback_query(call.id)
    bot.send_message(call.message.chat.id, STRINGS[lang]['ask_name'])

@bot.message_handler(func=lambda m: True)
def handle_text(message):
    lang = user_lang.get(message.chat.id, 'uz')
    name = message.text.strip()
    
    proc = bot.send_message(message.chat.id, STRINGS[lang]['searching'].format(name=name))
    players = get_player_list(name)
    bot.delete_message(message.chat.id, proc.message_id)
    
    if players:
        markup = types.InlineKeyboardMarkup(row_width=1)
        for p in players:
            markup.add(types.InlineKeyboardButton(text=f"🃏 {p['name']}", url=p['link']))
        bot.send_message(message.chat.id, f"{STRINGS[lang]['found'].format(name=name)}\n\n{STRINGS[lang]['guide']}", reply_markup=markup)
    else:
        bot.send_message(message.chat.id, STRINGS[lang]['not_found'])

# 4. SERVER
def run():
    app.run(host='0.0.0.0', port=8080)

if __name__ == "__main__":
    Thread(target=run).start()
    while True:
        try:
            bot.polling(none_stop=True, interval=0, timeout=20)
        except:
            time.sleep(5)
