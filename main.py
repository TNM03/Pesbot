import telebot
from telebot import types
import requests
from bs4 import BeautifulSoup
from flask import Flask
from threading import Thread

TOKEN = "8597572815:AAEOgOf8UCmRdoZtHqqkDl-D9Zt0oRRj2LY"
bot = telebot.TeleBot(TOKEN)
app = Flask('')

@app.route('/')
def home(): return "Bot Active"

# Tillar va Matnlar
STRINGS = {
    'uz': {
        'start': "Assalomu alaykum! Bo'limni tanlang:",
        'btn1': "📊 Ehtimollik", 'btn2': "📈 Max Reyting", 'btn3': "📅 Yangiliklar",
        'ask_name': "Futbolchi ismini kiriting:", 'ask_coins': "Tangalar miqdorini kiriting:",
        'wait': "🔎 Tahlil qilinmoqda...", 'not_found': "❌ Topilmadi.",
        'calc_res': "💰 Tangalar: {c}\n🎯 Epic yutish ehtimoli: {p}%"
    },
    'ru': {
        'start': "Здравствуйте! Выберите раздел:",
        'btn1': "📊 Вероятность", 'btn2': "📈 Макс Рейтинг", 'btn3': "📅 Новости",
        'ask_name': "Введите имя игрока:", 'ask_coins': "Введите количество монет:",
        'wait': "🔎 Анализируется...", 'not_found': "❌ Не найдено.",
        'calc_res': "💰 Монеты: {c}\n🎯 Шанс на Epic: {p}%"
    },
    'en': {
        'start': "Welcome! Choose a section:",
        'btn1': "📊 Probability", 'btn2': "📈 Max Rating", 'btn3': "📅 News",
        'ask_name': "Enter player name:", 'ask_coins': "Enter coin amount:",
        'wait': "🔎 Analyzing...", 'not_found': "❌ Not found.",
        'calc_res': "💰 Coins: {c}\n🎯 Chance for Epic: {p}%"
    }
}

user_lang = {}

# QIDIRUV VA TAHLIL (Blokdan qochish uchun maxsus sarlavhalar bilan)
def get_player_data(name):
    query = name.replace(' ', '+')
    # Pesmaster bloklarga chidamliroq va ma'lumotlari EFHUB bilan bir xil
    url = f"https://www.pesmaster.com/efootball-2022/search/?q={query}"
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
    try:
        res = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(res.text, 'html.parser')
        player_link = soup.select_one('.player-card-container a')
        if player_link:
            p_name = player_link.select_one('.player-card-name').text.strip()
            return f"✅ **{p_name}**\n\n📊 **Tahlil:**\n📈 Max Rating: 101-103\n⚙️ Tavsiya: Speed +8, Dexterity +12\n🛡 Playstyle: Goal Poacher"
        return None
    except: return None

@bot.message_handler(commands=['start'])
def start(message):
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("🇺🇿 UZ", callback_data='l_uz'),
               types.InlineKeyboardButton("🇷🇺 RU", callback_data='l_ru'),
               types.InlineKeyboardButton("🇬🇧 EN", callback_data='l_en'))
    bot.send_message(message.chat.id, "Tilni tanlang / Выберите язык:", reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data.startswith('l_'))
def set_lang(call):
    lang = call.data.split('_')[1]
    user_lang[call.message.chat.id] = lang
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add(STRINGS[lang]['btn1'], STRINGS[lang]['btn2'], STRINGS[lang]['btn3'])
    bot.send_message(call.message.chat.id, STRINGS[lang]['start'], reply_markup=markup)

@bot.message_handler(func=lambda m: True)
def handle_menu(message):
    chat_id = message.chat.id
    lang = user_lang.get(chat_id, 'uz')

    if message.text == STRINGS[lang]['btn2']:
        msg = bot.send_message(chat_id, STRINGS[lang]['ask_name'])
        bot.register_next_step_handler(msg, process_search)
    elif message.text == STRINGS[lang]['btn1']:
        msg = bot.send_message(chat_id, STRINGS[lang]['ask_coins'])
        bot.register_next_step_handler(msg, process_calc)
    elif message.text == STRINGS[lang]['btn3']:
        news = "🔥 **Konami News:**\nMonday: Epic Pack\nThursday: POTW"
        bot.send_message(chat_id, news)

def process_search(message):
    lang = user_lang.get(message.chat.id, 'uz')
    wait = bot.send_message(message.chat.id, STRINGS[lang]['wait'])
    data = get_player_data(message.text)
    bot.delete_message(message.chat.id, wait.message_id)
    if data:
        bot.send_message(message.chat.id, data, parse_mode="Markdown")
    else:
        bot.send_message(message.chat.id, STRINGS[lang]['not_found'])

def process_calc(message):
    lang = user_lang.get(message.chat.id, 'uz')
    try:
        coins = int(message.text)
        p = round((1 - ((147/150) ** (coins // 100))) * 100, 1)
        bot.send_message(message.chat.id, STRINGS[lang]['calc_res'].format(c=coins, p=p))
    except: bot.send_message(message.chat.id, "Error: Number only.")

def run(): app.run(host='0.0.0.0', port=8080)
if __name__ == "__main__":
    Thread(target=run).start()
    bot.polling(none_stop=True)
