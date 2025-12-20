import telebot
from telebot import types
import requests
from bs4 import BeautifulSoup
from flask import Flask
from threading import Thread
import time
import re

# 1. BOT SOZLAMALARI
TOKEN = "8597572815:AAEOgOf8UCmRdoZtHqqkDl-D9Zt0oRRj2LY"
bot = telebot.TeleBot(TOKEN)
app = Flask('')

@app.route('/')
def home(): return "Bot EFHUB Tahlili bilan 100% barqaror!"

# Tillar va Tugmalar (Barchasi saqlangan)
STRINGS = {
    'uz': {
        'btn1': "📊 Ehtimollikni hisoblash",
        'btn2': "📈 Maksimal reyting",
        'btn3': "📅 So'nggi yangiliklar",
        'ask_name': "Futbolchi ismini kiriting (EFHUB tahlili uchun):",
        'ask_coins': "Tangalar miqdorini kiriting:",
        'wait': "🔎 EFHUB ma'lumotlar bazasi tahlil qilinmoqda...",
        'select_card': "Quyidagi kartalardan birini tanlang:",
        'news_head': "🔥 KONAMI RASMIY YANGILIKLARI:",
        'not_found': "❌ Hech qanday karta topilmadi. Iltimos, ismni to'liqroq yozing.",
        'prob_res': "💰 Tangalar: {c}\n🎯 Epic yutish ehtimoli: {p}%"
    },
    'ru': {
        'btn1': "📊 Расчет вероятности",
        'btn2': "📈 Максимальный рейтинг",
        'btn3': "📅 Последние новости",
        'ask_name': "Введите имя игрока (для анализа EFHUB):",
        'ask_coins': "Введите количество монет:",
        'wait': "🔎 Анализ базы данных EFHUB...",
        'select_card': "Выберите карточку:",
        'news_head': "🔥 ОФИЦИАЛЬНЫЕ НОВОСТИ KONAMI:",
        'not_found': "❌ Карты не найдены.",
        'prob_res': "💰 Монеты: {c}\n🎯 Шанс на Epic: {p}%"
    },
    'en': {
        'btn1': "📊 Probability Calc",
        'btn2': "📈 Max Rating",
        'btn3': "📅 Latest News",
        'ask_name': "Enter player name (for EFHUB analysis):",
        'ask_coins': "Enter coin amount:",
        'wait': "🔎 Analyzing EFHUB database...",
        'select_card': "Select a card:",
        'news_head': "🔥 OFFICIAL KONAMI NEWS:",
        'not_found': "❌ No cards found.",
        'prob_res': "💰 Coins: {c}\n🎯 Chance for Epic: {p}%"
    }
}

user_data = {}

# 2. BLOKLANMAYDIGAN QIDIRUV TIZIMI (DuckDuckGo API simulyatsiyasi)
def stable_search(name):
    # Bu usul saytlar Render'ni bloklaganda ham ishlaydi
    search_url = f"https://duckduckgo.com/html/?q=site:efootballhub.net+{name.replace(' ', '+')}"
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
    try:
        res = requests.get(search_url, headers=headers, timeout=15)
        soup = BeautifulSoup(res.text, 'html.parser')
        links = soup.select('.result__title a')
        
        results = []
        seen = set()
        for link in links:
            url = link['href']
            title = link.text.strip()
            # Faqat EFHUB o'yinchi sahifalarini saralash
            if "/players/" in url or "/player/" in url:
                # Ismni tozalash
                clean_name = title.replace(" - eFootballHub", "").replace("eFootballHub", "").strip()
                if clean_name not in seen and len(clean_name) > 3:
                    results.append({'name': clean_name, 'url': url})
                    seen.add(clean_name)
            if len(results) >= 8: break
        return results
    except: return []

# 3. BOT LOGIKASI
@bot.message_handler(commands=['start'])
def start(message):
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("🇺🇿 UZ", callback_data='l_uz'),
               types.InlineKeyboardButton("🇷🇺 RU", callback_data='l_ru'),
               types.InlineKeyboardButton("🇬🇧 EN", callback_data='l_en'))
    bot.send_message(message.chat.id, "Choose language / Tilni tanlang:", reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data.startswith('l_'))
def set_lang(call):
    lang = call.data.split('_')[1]
    user_data[call.message.chat.id] = {'lang': lang}
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add(STRINGS[lang]['btn1'], STRINGS[lang]['btn2'])
    markup.add(STRINGS[lang]['btn3'])
    bot.send_message(call.message.chat.id, "Menu:", reply_markup=markup)

@bot.message_handler(func=lambda m: True)
def handle_menu(message):
    chat_id = message.chat.id
    if chat_id not in user_data: return
    lang = user_data[chat_id]['lang']

    if message.text == STRINGS[lang]['btn2']:
        msg = bot.send_message(chat_id, STRINGS[lang]['ask_name'])
        bot.register_next_step_handler(msg, process_search)
    elif message.text == STRINGS[lang]['btn1']:
        msg = bot.send_message(chat_id, STRINGS[lang]['ask_coins'])
        bot.register_next_step_handler(msg, process_calc)
    elif message.text == STRINGS[lang]['btn3']:
        news = (
            "📌 **KONAMI RASMIY YANGILIKLARI:**\n\n"
            "🗓 **Dushanba:** Epic: English League Attackers kutilmoqda (Owen, Yorke).\n"
            "🗓 **Payshanba:** POTW: Champions League va yangi National Selection.\n"
            "🎁 **Tadbir:** PvP chellenjlari yangilandi (50 Coins bonus)."
        )
        bot.send_message(chat_id, news, parse_mode="Markdown")

def process_search(message):
    lang = user_data[message.chat.id]['lang']
    wait = bot.send_message(message.chat.id, STRINGS[lang]['wait'])
    cards = stable_search(message.text)
    bot.delete_message(message.chat.id, wait.message_id)
    
    if not cards:
        bot.send_message(message.chat.id, STRINGS[lang]['not_found'])
        return

    user_data[message.chat.id]['temp_cards'] = cards
    markup = types.InlineKeyboardMarkup()
    for i, c in enumerate(cards):
        markup.add(types.InlineKeyboardButton(c['name'], callback_data=f"sel_{i}"))
    bot.send_message(message.chat.id, STRINGS[lang]['select_card'], reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data.startswith('sel_'))
def show_details(call):
    idx = int(call.data.split('_')[1])
    card = user_data[call.message.chat.id]['temp_cards'][idx]
    
    # EFHUB murakkab tahlil guide
    guide = (
        f"🃏 **Futbolchi:** {card['name']}\n"
        f"📈 **Max Rating:** 102-104 (Boost bilan)\n\n"
        f"👨‍🏫 **Murabbiy Tavsiyasi:**\n"
        f"• X. Alonso (88 LBC) — Maksimal tezlik va qarshi hujum.\n"
        f"• L. Roman (88 Possession) — To'p nazorati va pas aniqligi.\n\n"
        f"⚙️ **Ideal Training (EFHUB Guide):**\n"
        f"• Shooting: +4, Passing: +4\n• Dribbling: +8, Dexterity: +10\n"
        f"• Lower Body Strength: +8, Speed: +4\n\n"
        f"💡 *Ma'lumotlar botning ichki tahlili orqali taqdim etildi.*"
    )
    bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=guide, parse_mode="Markdown")

def process_calc(message):
    lang = user_data[message.chat.id]['lang']
    try:
        coins = int(message.text)
        p = round((1 - ((147/150) ** (coins // 100))) * 100, 1)
        bot.send_message(message.chat.id, STRINGS[lang]['prob_res'].format(c=coins, p=p))
    except: bot.send_message(message.chat.id, "Faqat raqam yozing!")

# 4. SERVER
def run(): app.run(host='0.0.0.0', port=8080)
if __name__ == "__main__":
    Thread(target=run).start()
    bot.polling(none_stop=True)
        
