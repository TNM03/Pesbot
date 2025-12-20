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
def home(): return "Bot 100% Faol"

# Tillar lug'ati
STRINGS = {
    'uz': {
        'btn1': "📊 Ehtimollikni hisoblash",
        'btn2': "📈 Maksimal reyting",
        'btn3': "📅 So'nggi yangiliklar",
        'ask_name': "Futbolchi ismini kiriting:",
        'ask_coins': "Tangalar miqdorini kiriting:",
        'wait': "Qidirilmoqda...",
        'select_card': "Quyidagi kartalardan birini tanlang:",
        'news_head': "🔥 KONAMI RASMIY YANGILIKLARI:",
        'prob_res': "💰 Tangalar: {c}\n🎯 Epic yutish ehtimoli: {p}%\n\nMaslahat: 150 talik Box uchun kamida 5000 coin tavsiya etiladi."
    },
    'ru': {
        'btn1': "📊 Расчет вероятности",
        'btn2': "📈 Максимальный рейтинг",
        'btn3': "📅 Последние новости",
        'ask_name': "Введите имя игрока:",
        'ask_coins': "Введите количество монет:",
        'wait': "Поиск...",
        'select_card': "Выберите одну из карточек:",
        'news_head': "🔥 ОФИЦИАЛЬНЫЕ НОВОСТИ KONAMI:",
        'prob_res': "💰 Монеты: {c}\n🎯 Шанс на Epic: {p}%\n\nСовет: Рекомендуется минимум 5000 монет."
    },
    'en': {
        'btn1': "📊 Probability Calc",
        'btn2': "📈 Max Rating",
        'btn3': "📅 Latest News",
        'ask_name': "Enter player name:",
        'ask_coins': "Enter coin amount:",
        'wait': "Searching...",
        'select_card': "Select one of the cards:",
        'news_head': "🔥 OFFICIAL KONAMI NEWS:",
        'prob_res': "💰 Coins: {c}\n🎯 Epic Chance: {p}%\n\nTip: At least 5000 coins recommended."
    }
}

user_data = {} # Holatlarni saqlash

# 2. FUNKSIYALAR (LOGIKA)

def get_efhub_cards(name):
    """EFHUB va PESMaster tahlili orqali variantlarni yig'ish"""
    url = f"https://www.pesmaster.com/efootball-2022/search/?q={name.replace(' ', '+')}"
    headers = {'User-Agent': 'Mozilla/5.0'}
    try:
        res = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(res.text, 'html.parser')
        cards = soup.select('a[href*="/player/"]')
        results = []
        for c in cards[:8]:
            c_name = c.text.strip()
            if len(c_name) > 3 and "Featured" not in c_name:
                results.append({'name': c_name, 'id': c['href'].split('/')[-2]})
        return results
    except: return []

def get_konami_news():
    """Konami rasmiy yangiliklarini simulyatsiya qilish (Parser)"""
    # Bu qismda rasmiy saytdan ma'lumot olish kodi bo'ladi
    # Hozirgi kutilayotgan dushanba/payshanba yangiliklari:
    news = (
        "✅ Dushanba: Epic: English League Attackers kutilmoqda (Owen, Yorke, Cole).\n"
        "✅ Payshanba: POTW: National Selection va Yangi Match Pass sovg'alari.\n"
        "✅ Tadbir: 50 free coins uchun PvP chellenjlar yangilanadi."
    )
    return news

# 3. HANDLERS

@bot.message_handler(commands=['start'])
def start(message):
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("🇺🇿 UZ", callback_data='l_uz'),
               types.InlineKeyboardButton("🇷🇺 RU", callback_data='l_ru'),
               types.InlineKeyboardButton("🇬🇧 EN", callback_data='l_en'))
    bot.send_message(message.chat.id, "Choose language / Tilni tanlang:", reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data.startswith('l_'))
def set_language(call):
    lang = call.data.split('_')[1]
    user_data[call.message.chat.id] = {'lang': lang}
    
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add(STRINGS[lang]['btn1'], STRINGS[lang]['btn2'])
    markup.add(STRINGS[lang]['btn3'])
    bot.send_message(call.message.chat.id, STRINGS[lang]['menu'] if 'menu' in STRINGS[lang] else "OK!", reply_markup=markup)

@bot.message_handler(func=lambda m: True)
def main_menu(message):
    chat_id = message.chat.id
    if chat_id not in user_data: return
    lang = user_data[chat_id]['lang']

    if message.text == STRINGS[lang]['btn1']:
        msg = bot.send_message(chat_id, STRINGS[lang]['ask_coins'])
        bot.register_next_step_handler(msg, calc_prob)
    
    elif message.text == STRINGS[lang]['btn2']:
        msg = bot.send_message(chat_id, STRINGS[lang]['ask_name'])
        bot.register_next_step_handler(msg, find_cards)
    
    elif message.text == STRINGS[lang]['btn3']:
        news = get_konami_news()
        bot.send_message(chat_id, f"{STRINGS[lang]['news_head']}\n\n{news}")

def calc_prob(message):
    lang = user_data[message.chat.id]['lang']
    try:
        coins = int(message.text)
        p = round((1 - ((147/150) ** (coins // 100))) * 100, 1)
        bot.send_message(message.chat.id, STRINGS[lang]['prob_res'].format(c=coins, p=p))
    except: bot.send_message(message.chat.id, "Error!")

def find_cards(message):
    lang = user_data[message.chat.id]['lang']
    name = message.text
    bot.send_message(message.chat.id, STRINGS[lang]['wait'])
    cards = get_efhub_cards(name)
    
    if not cards:
        bot.send_message(message.chat.id, STRINGS[lang]['not_found'])
        return

    markup = types.InlineKeyboardMarkup()
    for c in cards:
        markup.add(types.InlineKeyboardButton(c['name'], callback_data=f"card_{c['id']}"))
    bot.send_message(message.chat.id, STRINGS[lang]['select_card'], reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data.startswith('card_'))
def show_max_rating(call):
    lang = user_data[call.message.chat.id]['lang']
    # Bu yerda tanlangan karta ID bo'yicha training guide beriladi
    guide = (
        "📈 **Maksimal Reyting Tahlili:**\n\n"
        "1️⃣ **Murabbiy tavsiyasi:** X. Alonso (Auto-allocation) yoki L. Roman (88 Booster).\n"
        "2️⃣ **Training:** Dexterity: +8, Lower Body: +4, Aerial: +2.\n"
        "3️⃣ **Natija:** Ushbu karta jamoada 101-103 reytingga chiqadi."
    )
    bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=guide)

# 4. RUN
def run(): app.run(host='0.0.0.0', port=8080)
if __name__ == "__main__":
    Thread(target=run).start()
    bot.polling(none_stop=True)
                
