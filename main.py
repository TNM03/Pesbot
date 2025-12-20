import telebot
from telebot import types
import requests
from bs4 import BeautifulSoup
from flask import Flask
from threading import Thread

# SOZLAMALAR
TOKEN = "8597572815:AAEOgOf8UCmRdoZtHqqkDl-D9Zt0oRRj2LY"
SCRAPER_API_KEY = "75416d669ddf160668872e638d11f605"
bot = telebot.TeleBot(TOKEN)
app = Flask('')

@app.route('/')
def home(): return "Bot Active with ScraperAPI"

STRINGS = {
    'uz': {
        'start': "Assalomu alaykum! Tilni tanlang:",
        'btn1': "📊 Ehtimollik", 'btn2': "📈 Max Reyting", 'btn3': "📅 Yangiliklar",
        'ask_name': "Futbolchi ismini inglizcha kiriting (masalan: Messi):",
        'ask_coins': "Tangalar miqdorini kiriting:",
        'wait': "🔎 ScraperAPI orqali tahlil qilinmoqda (15-20 soniya kuting)...",
        'not_found': "❌ Futbolchi topilmadi.",
        'calc_res': "💰 Tangalar: {c}\n🎯 Epic yutish ehtimoli: {p}%"
    },
    'ru': {
        'start': "Здравствуйте! Выберите язык:",
        'btn1': "📊 Вероятность", 'btn2': "📈 Макс Рейтинг", 'btn3': "📅 Новости",
        'ask_name': "Введите имя игрока (на английском):",
        'ask_coins': "Введите количество монет:",
        'wait': "🔎 Анализ через ScraperAPI (подождите 15-20 сек)...",
        'not_found': "❌ Игрок не найден.",
        'calc_res': "💰 Монеты: {c}\n🎯 Шанс на Epic: {p}%"
    }
}

user_lang = {}

def get_player_stats(name):
    search_url = f"https://www.pesmaster.com/efootball-2022/search/?q={name.replace(' ', '+')}"
    proxy_url = f"http://api.scraperapi.com?api_key={SCRAPER_API_KEY}&url={search_url}"
    try:
        res = requests.get(proxy_url, timeout=25)
        soup = BeautifulSoup(res.text, 'html.parser')
        player_card = soup.select_one('.player-card-container a')
        if player_card:
            p_name = player_card.select_one('.player-card-name').text.strip()
            # Bot ichida ko'rsatiladigan tahlil matni
            return f"✅ **{p_name}** topildi!\n\n📈 **Max Rating:** 101-104\n⚙️ **Tavsiya:** Speed +8, Dexterity +12, Lower Body +8\n📖 **Tahlil:** Bu karta hozirgi metada eng yaxshilardan biri."
        return None
    except: return None

@bot.message_handler(commands=['start'])
def start(message):
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("🇺🇿 O'zbekcha", callback_data='l_uz'),
               types.InlineKeyboardButton("🇷🇺 Русский", callback_data='l_ru'))
    bot.send_message(message.chat.id, STRINGS['uz']['start'], reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data.startswith('l_'))
def set_lang(call):
    lang = call.data.split('_')[1]
    user_lang[call.message.chat.id] = lang
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add(STRINGS[lang]['btn1'], STRINGS[lang]['btn2'], STRINGS[lang]['btn3'])
    bot.send_message(call.message.chat.id, "Bo'limni tanlang:", reply_markup=markup)

@bot.message_handler(func=lambda m: True)
def handle_menu(message):
    lang = user_lang.get(message.chat.id, 'uz')
    if message.text in [STRINGS['uz']['btn2'], STRINGS['ru']['btn2']]:
        msg = bot.send_message(message.chat.id, STRINGS[lang]['ask_name'])
        bot.register_next_step_handler(msg, process_search)
    elif message.text in [STRINGS['uz']['btn1'], STRINGS['ru']['btn1']]:
        msg = bot.send_message(message.chat.id, STRINGS[lang]['ask_coins'])
        bot.register_next_step_handler(msg, process_calc)
    elif message.text in [STRINGS['uz']['btn3'], STRINGS['ru']['btn3']]:
        bot.send_message(message.chat.id, "📅 **Yangiliklar:**\nDushanba: Epic Pack\nPayshanba: POTW Update")

def process_search(message):
    lang = user_lang.get(message.chat.id, 'uz')
    wait = bot.send_message(message.chat.id, STRINGS[lang]['wait'])
    data = get_player_stats(message.text)
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
    except: bot.send_message(message.chat.id, "Faqat raqam kiriting!")

def run(): app.run(host='0.0.0.0', port=8080)
if __name__ == "__main__":
    Thread(target=run).start()
    bot.polling(none_stop=True)
