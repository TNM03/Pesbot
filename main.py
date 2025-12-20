import telebot
from telebot import types

TOKEN = "8597572815:AAEOgOf8UCmRdoZtHqqkDl-D9Zt0oRRj2LY"
bot = telebot.TeleBot(TOKEN)

# Matnlar bazasi
STRINGS = {
    'uz': {
        'start': "Tilni tanlang:",
        'menu': "Bo'limni tanlang:",
        'btn1': "📊 Ehtimollik", 'btn2': "📈 Max Reyting", 'btn3': "📅 Yangiliklar",
        'ask_name': "Futbolchi ismini inglizcha kiriting:",
        'ask_coins': "Tangalar miqdorini kiriting:",
        'calc_res': "💰 Tangalar: {c}\n🎯 Epic yutish ehtimoli: {p}%"
    },
    'ru': {
        'start': "Выберите язык:",
        'menu': "Выберите раздел:",
        'btn1': "📊 Вероятность", 'btn2': "📈 Макс Рейтинг", 'btn3': "📅 Новости",
        'ask_name': "Введите имя игрока (на английском):",
        'ask_coins': "Введите количество монет:",
        'calc_res': "💰 Монеты: {c}\n🎯 Шанс на Epic: {p}%"
    }
}

user_data = {}

@bot.message_handler(commands=['start'])
def start(message):
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("🇺🇿 O'zbekcha", callback_data='lang_uz'),
               types.InlineKeyboardButton("🇷🇺 Русский", callback_data='lang_ru'))
    bot.send_message(message.chat.id, "Select Language / Tilni tanlang:", reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data.startswith('lang_'))
def set_language(call):
    lang = call.data.split('_')[1]
    user_data[call.message.chat.id] = lang
    show_menu(call.message.chat.id, lang)

def show_menu(chat_id, lang):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add(STRINGS[lang]['btn1'], STRINGS[lang]['btn2'])
    markup.add(STRINGS[lang]['btn3'])
    bot.send_message(chat_id, STRINGS[lang]['menu'], reply_markup=markup)

@bot.message_handler(func=lambda m: True)
def handle_text(message):
    lang = user_data.get(message.chat.id, 'uz')
    
    if message.text in [STRINGS['uz']['btn1'], STRINGS['ru']['btn1']]:
        bot.send_message(message.chat.id, STRINGS[lang]['ask_coins'])
    
    elif message.text in [STRINGS['uz']['btn2'], STRINGS['ru']['btn2']]:
        bot.send_message(message.chat.id, STRINGS[lang]['ask_name'])
        bot.register_next_step_handler(message, process_player_search)
        
    elif message.text in [STRINGS['uz']['btn3'], STRINGS['ru']['btn3']]:
        news = "🔥 **Konami News:**\nMonday: Epic Box\nThursday: POTW"
        bot.send_message(message.chat.id, news, parse_mode="Markdown")

    elif message.text.isdigit():
        coins = int(message.text)
        p = round((1 - ((147/150) ** (coins // 100))) * 100, 1)
        bot.send_message(message.chat.id, STRINGS[lang]['calc_res'].format(c=coins, p=p))

def process_player_search(message):
    lang = user_data.get(message.chat.id, 'uz')
    name = message.text.replace(' ', '+')
    # Blokirovka bo'lmasligi uchun to'g'ridan-to'g'ri link generatsiya qilamiz
    link = f"https://efootballhub.net/efootball23/search/players?searchQuery={name}"
    
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("🔍 EFHUB Natijalarini ko'rish", url=link))
    
    bot.send_message(message.chat.id, f"✅ **{message.text}** tahlili tayyor!", reply_markup=markup, parse_mode="Markdown")

if __name__ == "__main__":
    bot.polling(none_stop=True)
