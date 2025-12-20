import telebot
from telebot import types
import requests
from bs4 import BeautifulSoup
import json
import re

# Bot tokeningizni kiriting
BOT_TOKEN = "8597572815:AAEOgOf8UCmRdoZtHqqkDl-D9Zt0oRRj2LY"
bot = telebot.TeleBot(BOT_TOKEN)

# Foydalanuvchi tillari
user_language = {}

# Tarjimalar
translations = {
    'uz': {
        'welcome': '⚽ PES/eFootball botiga xush kelibsiz!\n\nTilni tanlang:',
        'main_menu': '🎮 Asosiy menyu\n\nKerakli bo\'limni tanlang:',
        'prob_calc': '🎲 Ehtimollikni hisoblash',
        'max_rating': '📊 Maksimal reyting',
        'news': '📰 So\'nggi yangiliklar',
        'back': '🔙 Orqaga',
        'choose_player': '⚽ Futbolchi nomini kiriting:',
        'searching': '🔍 Qidirilmoqda...',
        'player_cards': '📋 {} ning kartalari:\n\nKerakli kartani tanlang:',
        'no_results': '❌ Natija topilmadi. Iltimos, to\'g\'ri nom kiriting.',
        'calculating': '⏳ Hisoblanmoqda...',
        'max_rating_info': '📊 {} - Maksimal Reyting\n\n🎯 Maksimal reyting: {}\n\n👔 Eng yaxshi murabbiylar:\n{}\n\n💪 Tavsiya etiladigan mashg\'ulotlar:\n{}\n\n⚡ Qo\'shimcha maslahatlar:\n{}',
        'news_loading': '📰 Yangiliklar yuklanmoqda...',
        'latest_news': '📰 So\'nggi yangiliklar\n\n{}',
        'pack_type': '📦 Pack turini tanlang:',
        'standard': '⚪ Standart Pack',
        'featured': '🌟 Featured Pack',
        'legend': '👑 Legend Pack',
        'prob_result': '🎲 Ehtimolliklar:\n\n⚫ Black Ball: {}%\n🥇 Gold Ball: {}%\n🥈 Silver Ball: {}%\n🟡 Bronze Ball: {}%'
    },
    'ru': {
        'welcome': '⚽ Добро пожаловать в PES/eFootball бот!\n\nВыберите язык:',
        'main_menu': '🎮 Главное меню\n\nВыберите раздел:',
        'prob_calc': '🎲 Расчет вероятности',
        'max_rating': '📊 Максимальный рейтинг',
        'news': '📰 Последние новости',
        'back': '🔙 Назад',
        'choose_player': '⚽ Введите имя игрока:',
        'searching': '🔍 Поиск...',
        'player_cards': '📋 Карточки {}:\n\nВыберите нужную карточку:',
        'no_results': '❌ Результаты не найдены. Пожалуйста, введите правильное имя.',
        'calculating': '⏳ Расчет...',
        'max_rating_info': '📊 {} - Максимальный Рейтинг\n\n🎯 Максимальный рейтинг: {}\n\n👔 Лучшие тренеры:\n{}\n\n💪 Рекомендуемые тренировки:\n{}\n\n⚡ Дополнительные советы:\n{}',
        'news_loading': '📰 Загрузка новостей...',
        'latest_news': '📰 Последние новости\n\n{}',
        'pack_type': '📦 Выберите тип пака:',
        'standard': '⚪ Стандартный Pack',
        'featured': '🌟 Featured Pack',
        'legend': '👑 Legend Pack',
        'prob_result': '🎲 Вероятности:\n\n⚫ Black Ball: {}%\n🥇 Gold Ball: {}%\n🥈 Silver Ball: {}%\n🟡 Bronze Ball: {}%'
    },
    'en': {
        'welcome': '⚽ Welcome to PES/eFootball bot!\n\nChoose language:',
        'main_menu': '🎮 Main Menu\n\nSelect section:',
        'prob_calc': '🎲 Probability Calculator',
        'max_rating': '📊 Max Rating',
        'news': '📰 Latest News',
        'back': '🔙 Back',
        'choose_player': '⚽ Enter player name:',
        'searching': '🔍 Searching...',
        'player_cards': '📋 {} cards:\n\nSelect the card:',
        'no_results': '❌ No results found. Please enter correct name.',
        'calculating': '⏳ Calculating...',
        'max_rating_info': '📊 {} - Max Rating\n\n🎯 Maximum rating: {}\n\n👔 Best managers:\n{}\n\n💪 Recommended training:\n{}\n\n⚡ Additional tips:\n{}',
        'news_loading': '📰 Loading news...',
        'latest_news': '📰 Latest News\n\n{}',
        'pack_type': '📦 Select pack type:',
        'standard': '⚪ Standard Pack',
        'featured': '🌟 Featured Pack',
        'legend': '👑 Legend Pack',
        'prob_result': '🎲 Probabilities:\n\n⚫ Black Ball: {}%\n🥇 Gold Ball: {}%\n🥈 Silver Ball: {}%\n🟡 Bronze Ball: {}%'
    }
}

# eFootball Hub ma'lumotlar bazasi (real scraping o'rniga)
player_database = {
    'messi': {
        'cards': ['Base', 'Featured', 'Iconic Moment'],
        'base_rating': 93,
        'max_ratings': {
            'Base': 95,
            'Featured': 97,
            'Iconic Moment': 98
        },
        'best_managers': {
            'Base': ['Pep Guardiola (4-3-3)', 'Diego Simeone (4-4-2)', 'Jurgen Klopp (4-3-3)'],
            'Featured': ['Pep Guardiola (4-3-3)', 'Roberto Martinez (3-4-3)', 'Jurgen Klopp (4-3-3)'],
            'Iconic Moment': ['Pep Guardiola (4-3-3)', 'Johan Cruyff (4-3-3)', 'Arsene Wenger (4-2-3-1)']
        },
        'training': {
            'Base': ['Dribbling Training (x10)', 'Finishing Training (x8)', 'Speed Training (x5)'],
            'Featured': ['Dribbling Training (x12)', 'Finishing Training (x10)', 'Passing Training (x8)'],
            'Iconic Moment': ['Dribbling Training (x15)', 'Finishing Training (x12)', 'Ball Control (x10)']
        },
        'tips': {
            'Base': 'SS pozitsiyasida o\'ynating. Attacking Prowess skilini faollashtiring.',
            'Featured': 'RWF yoki SS pozitsiyasida maksimal samara beradi. Advanced Instructions: Counter Attack.',
            'Iconic Moment': 'CF yoki SS pozitsiyasida juda kuchli. Playstyle: Creative Playmaker.'
        }
    },
    'ronaldo': {
        'cards': ['Base', 'Featured', 'Iconic Moment'],
        'base_rating': 92,
        'max_ratings': {
            'Base': 94,
            'Featured': 96,
            'Iconic Moment': 99
        },
        'best_managers': {
            'Base': ['Zinedine Zidane (4-3-3)', 'Diego Simeone (4-4-2)', 'Antonio Conte (3-5-2)'],
            'Featured': ['Zinedine Zidane (4-3-3)', 'Jose Mourinho (4-2-3-1)', 'Carlo Ancelotti (4-3-3)'],
            'Iconic Moment': ['Sir Alex Ferguson (4-4-2)', 'Zinedine Zidane (4-3-3)', 'Massimiliano Allegri (4-3-3)']
        },
        'training': {
            'Base': ['Physical Training (x10)', 'Finishing Training (x10)', 'Speed Training (x8)'],
            'Featured': ['Physical Training (x12)', 'Finishing Training (x12)', 'Header Training (x8)'],
            'Iconic Moment': ['Physical Training (x15)', 'Finishing Training (x15)', 'Speed & Header (x10)']
        },
        'tips': {
            'Base': 'LWF yoki CF pozitsiyasida o\'ynating. Goal Poacher playstyle.',
            'Featured': 'CF pozitsiyasida eng kuchli. Counter Target faollashtiring.',
            'Iconic Moment': 'CF yoki LWF da hujum etuvchi sifatida ishlatiladi. Skill: Acrobatic Finishing.'
        }
    },
    'neymar': {
        'cards': ['Base', 'Featured', 'Iconic Moment'],
        'base_rating': 91,
        'max_ratings': {
            'Base': 93,
            'Featured': 95,
            'Iconic Moment': 96
        },
        'best_managers': {
            'Base': ['Pep Guardiola (4-3-3)', 'Thomas Tuchel (3-4-3)', 'Mauricio Pochettino (4-2-3-1)'],
            'Featured': ['Pep Guardiola (4-3-3)', 'Luis Enrique (4-3-3)', 'Thomas Tuchel (3-4-3)'],
            'Iconic Moment': ['Pep Guardiola (4-3-3)', 'Luis Enrique (4-3-3)', 'Johan Cruyff (4-3-3)']
        },
        'training': {
            'Base': ['Dribbling Training (x12)', 'Speed Training (x8)', 'Passing Training (x6)'],
            'Featured': ['Dribbling Training (x15)', 'Speed Training (x10)', 'Finishing Training (x8)'],
            'Iconic Moment': ['Dribbling Training (x18)', 'Speed Training (x12)', 'Ball Control (x10)']
        },
        'tips': {
            'Base': 'LWF yoki AMF da o\'ynating. Skills: Double Touch, Flip Flap.',
            'Featured': 'LWF pozitsiyasida kreativlik maksimal. Playstyle: Prolific Winger.',
            'Iconic Moment': 'LWF yoki SS da juda xavfli. Advanced: Quick Counter + Possession.'
        }
    }
}

def get_text(user_id, key):
    lang = user_language.get(user_id, 'en')
    return translations[lang].get(key, key)

@bot.message_handler(commands=['start'])
def start(message):
    markup = types.InlineKeyboardMarkup(row_width=3)
    btn_uz = types.InlineKeyboardButton("🇺🇿 O'zbekcha", callback_data='lang_uz')
    btn_ru = types.InlineKeyboardButton("🇷🇺 Русский", callback_data='lang_ru')
    btn_en = types.InlineKeyboardButton("🇬🇧 English", callback_data='lang_en')
    markup.add(btn_uz, btn_ru, btn_en)
    
    bot.send_message(message.chat.id, "⚽ Welcome! | Добро пожаловать! | Xush kelibsiz!", reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data.startswith('lang_'))
def set_language(call):
    lang = call.data.split('_')[1]
    user_language[call.message.chat.id] = lang
    bot.answer_callback_query(call.id)
    show_main_menu(call.message.chat.id, call.message.message_id)

def show_main_menu(chat_id, message_id=None):
    markup = types.InlineKeyboardMarkup(row_width=1)
    btn1 = types.InlineKeyboardButton(get_text(chat_id, 'prob_calc'), callback_data='probability')
    btn2 = types.InlineKeyboardButton(get_text(chat_id, 'max_rating'), callback_data='max_rating')
    btn3 = types.InlineKeyboardButton(get_text(chat_id, 'news'), callback_data='news')
    markup.add(btn1, btn2, btn3)
    
    text = get_text(chat_id, 'main_menu')
    if message_id:
        bot.edit_message_text(text, chat_id, message_id, reply_markup=markup)
    else:
        bot.send_message(chat_id, text, reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data == 'probability')
def probability_handler(call):
    bot.answer_callback_query(call.id)
    markup = types.InlineKeyboardMarkup(row_width=1)
    btn1 = types.InlineKeyboardButton(get_text(call.message.chat.id, 'standard'), callback_data='prob_standard')
    btn2 = types.InlineKeyboardButton(get_text(call.message.chat.id, 'featured'), callback_data='prob_featured')
    btn3 = types.InlineKeyboardButton(get_text(call.message.chat.id, 'legend'), callback_data='prob_legend')
    btn_back = types.InlineKeyboardButton(get_text(call.message.chat.id, 'back'), callback_data='back_main')
    markup.add(btn1, btn2, btn3, btn_back)
    
    bot.edit_message_text(get_text(call.message.chat.id, 'pack_type'), call.message.chat.id, call.message.message_id, reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data.startswith('prob_'))
def show_probability(call):
    bot.answer_callback_query(call.id)
    pack_type = call.data.split('_')[1]
    
    probabilities = {
        'standard': {'black': 5, 'gold': 25, 'silver': 40, 'bronze': 30},
        'featured': {'black': 15, 'gold': 35, 'silver': 30, 'bronze': 20},
        'legend': {'black': 40, 'gold': 35, 'silver': 20, 'bronze': 5}
    }
    
    probs = probabilities[pack_type]
    text = get_text(call.message.chat.id, 'prob_result').format(
        probs['black'], probs['gold'], probs['silver'], probs['bronze']
    )
    
    markup = types.InlineKeyboardMarkup()
    btn_back = types.InlineKeyboardButton(get_text(call.message.chat.id, 'back'), callback_data='back_main')
    markup.add(btn_back)
    
    bot.edit_message_text(text, call.message.chat.id, call.message.message_id, reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data == 'max_rating')
def max_rating_handler(call):
    bot.answer_callback_query(call.id)
    msg = bot.edit_message_text(get_text(call.message.chat.id, 'choose_player'), call.message.chat.id, call.message.message_id)
    bot.register_next_step_handler(msg, process_player_name)

def process_player_name(message):
    player_name = message.text.lower().strip()
    
    bot.send_message(message.chat.id, get_text(message.chat.id, 'searching'))
    
    # Ma'lumotlar bazasidan qidirish
    player_data = None
    for key in player_database.keys():
        if player_name in key or key in player_name:
            player_data = player_database[key]
            break
    
    if not player_data:
        markup = types.InlineKeyboardMarkup()
        btn_back = types.InlineKeyboardButton(get_text(message.chat.id, 'back'), callback_data='back_main')
        markup.add(btn_back)
        bot.send_message(message.chat.id, get_text(message.chat.id, 'no_results'), reply_markup=markup)
        return
    
    # Kartalarni ko'rsatish
    markup = types.InlineKeyboardMarkup(row_width=1)
    for card in player_data['cards']:
        btn = types.InlineKeyboardButton(f"⚽ {card}", callback_data=f'card_{player_name}_{card}')
        markup.add(btn)
    btn_back = types.InlineKeyboardButton(get_text(message.chat.id, 'back'), callback_data='back_main')
    markup.add(btn_back)
    
    bot.send_message(message.chat.id, get_text(message.chat.id, 'player_cards').format(player_name.capitalize()), reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data.startswith('card_'))
def show_max_rating(call):
    bot.answer_callback_query(call.id)
    _, player_name, card_type = call.data.split('_', 2)
    
    bot.edit_message_text(get_text(call.message.chat.id, 'calculating'), call.message.chat.id, call.message.message_id)
    
    player_data = None
    for key in player_database.keys():
        if player_name in key:
            player_data = player_database[key]
            break
    
    if player_data:
        max_rating = player_data['max_ratings'][card_type]
        managers = '\n'.join([f"👔 {m}" for m in player_data['best_managers'][card_type]])
        training = '\n'.join([f"💪 {t}" for t in player_data['training'][card_type]])
        tips = player_data['tips'][card_type]
        
        text = get_text(call.message.chat.id, 'max_rating_info').format(
            f"{player_name.capitalize()} ({card_type})",
            max_rating,
            managers,
            training,
            tips
        )
        
        markup = types.InlineKeyboardMarkup()
        btn_back = types.InlineKeyboardButton(get_text(call.message.chat.id, 'back'), callback_data='back_main')
        markup.add(btn_back)
        
        bot.edit_message_text(text, call.message.chat.id, call.message.message_id, reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data == 'news')
def news_handler(call):
    bot.answer_callback_query(call.id)
    bot.edit_message_text(get_text(call.message.chat.id, 'news_loading'), call.message.chat.id, call.message.message_id)
    
    # Real yangiliklar (Konami rasmiy saytidan olingan ma'lumotlar simulatsiyasi)
    news_data = """🔥 Dushanba (23-dekabr) yangiliklari:

⚽ YANGI FEATURED PLAYERS
• Mbappe (PSG) - 97 reyting
• Haaland (Man City) - 96 reyting
• Vinicius Jr (Real Madrid) - 95 reyting

🎮 YANGI HODISA
"Winter Festival" hodisasi boshlanadi!
• 14 kun davom etadi
• Maxsus login bonuslari
• 3x GP mukofotlari

👑 ICONIC MOMENT PACK
• Zidane (Real Madrid Legend)
• Ronaldinho (Barcelona Legend)
• Iniesta (Barcelona Legend)

💰 MAXSUS TAKLIF
• 50% chegirma coinlarga
• 100,000 GP bepul
• 10x Featured Player Spin

📅 Payshanba (26-dekabr) kutilayotgan yangiliklar:

⭐ CLUB SELECTION
• Manchester City
• Real Madrid
• Bayern Munich

🏆 MATCHDAY HODISASI
• England League
• La Liga Spain
• Serie A Italy

💎 YANGI PLAYSTYLE
"Deep-Lying Forward" qo'shiladi

⚡ TIZIM YANGILANISHI
• Yangi animatsiyalar
• Grafika yaxshi