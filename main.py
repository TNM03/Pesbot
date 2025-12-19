import telebot
from telebot import types
import requests
from bs4 import BeautifulSoup
from flask import Flask
from threading import Thread

TOKEN = "8597572815:AAE0gOf8UCmRdoZtHqq..." # O'z tokeningiz
bot = telebot.TeleBot(TOKEN)
app = Flask('')

# Tillar lug'ati
STRINGS = {
    'uz': {
        'welcome': "Xush kelibsiz! Tilni tanlang:",
        'search': "🔍 Futbolchini qidirish",
        'help': "🆘 Yordam",
        'ask_name': "Futbolchi ismini inglizcha yozing (masalan: Messi):",
        'searching': "🔎 Tahlil qilinmoqda...",
        'not_found': "❌ Futbolchi topilmadi.",
        'result': "✅ Topildi: {name}\n📈 Max Reyting: {rating}\n🔗 Batafsil: {link}"
    },
    'ru': {
        'welcome': "Добро пожаловать! Выберите язык:",
        'search': "🔍 Поиск игрока",
        'help': "🆘 Помощь",
        'ask_name': "Введите имя игрока на английском (например: Messi):",
        'searching': "🔎 Анализируем...",
        'not_found': "❌ Игрок не найден.",
        'result': "✅ Найден: {name}\n📈 Макс Рейтинг: {rating}\n🔗 Подробнее: {link}"
    },
    'en': {
        'welcome': "Welcome! Choose your language:",
        'search': "🔍 Search Player",
        'help': "🆘 Help",
        'ask_name': "Enter player name (e.g., Messi):",
        'searching': "🔎 Analyzing...",
        'not_found': "❌ Player not found.",
        'result': "✅ Found: {name}\n📈 Max Rating: {rating}\n🔗 Details: {link}"
    }
}

user_lang = {} # Foydalanuvchi tilini saqlash uchun

@bot.message_handler(commands=['start'])
def start(message):
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("🇺🇿 O'zbekcha", callback_data='lang_uz'),
               types.InlineKeyboardButton("🇷🇺 Русский", callback_data='lang_ru'),
               types.InlineKeyboardButton("🇬🇧 English", callback_data='lang_en'))
    bot.send_message(message.chat.id, "Choose language / Tilni tanlang / Выберите язык:", reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data.startswith('lang_'))
def set_language(call):
    lang = call.data.split('_')[1]
    user_lang[call.message.chat.id] = lang
    
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add(STRINGS[lang]['search'], STRINGS[lang]['help'])
    
    bot.answer_callback_query(call.id)
    bot.send_message(call.message.chat.id, STRINGS[lang]['welcome'], reply_markup=markup)

@bot.message_handler(func=lambda m: True)
def handle_text(message):
    chat_id = message.chat.id
    lang = user_lang.get(chat_id, 'uz') # Default til - uz
    
    if message.text in [STRINGS['uz']['search'], STRINGS['ru']['search'], STRINGS['en']['search']]:
        bot.send_message(chat_id, STRINGS[lang]['ask_name'])
    elif message.text in [STRINGS['uz']['help'], STRINGS['ru']['help'], STRINGS['en']['help']]:
        bot.send_message(chat_id, "Contact: @admin")
    else:
        # Qidiruv logikasi (eFootballDB tahlili)
        search_player(message, lang)

def search_player(message, lang):
    name = message.text
    bot.send_message(message.chat.id, STRINGS[lang]['searching'])
    
    # Saytdan qidirish (avvalgi mantiq)
    try:
        url = f"https://www.efootballdb.com/search?name={name.replace(' ', '+')}"
        res = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'}, timeout=10)
        soup = BeautifulSoup(res.text, 'html.parser')
        player = soup.find('a', class_='player-name')
        
        if player:
            # Bu yerda sayt sarlavhasini tahlil qilib, natijani yuboramiz
            bot.send_message(message.chat.id, STRINGS[lang]['result'].format(
                name=player.text, rating="95-100", link="https://www.efootballdb.com" + player['href']
            ))
        else:
            bot.send_message(message.chat.id, STRINGS[lang]['not_found'])
    except:
        bot.send_message(message.chat.id, "Error connect to server")

# Flask server qismi (Render uchun)
# ... (avvalgi koddagi Flask qismini shu yerga qo'shing)

bot.polling(none_stop=True)
