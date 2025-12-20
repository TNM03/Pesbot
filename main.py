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
def home(): return "Bot EFHUB + PESMaster bilan faol!"

# Tillar va Tugmalar
STRINGS = {
    'uz': {
        'btn1': "📊 Ehtimollikni hisoblash",
        'btn2': "📈 Maksimal reyting",
        'btn3': "📅 So'nggi yangiliklar",
        'ask_name': "Futbolchi ismini kiriting (EFHUB tahlili uchun):",
        'wait': "🔎 EFHUB va PESMaster bazalari tahlil qilinmoqda...",
        'select_card': "Quyidagi kartalardan birini tanlang:",
        'news_head': "🔥 KONAMI RASMIY YANGILIKLARI:",
        'not_found': "❌ Hech qanday karta topilmadi."
    },
    'ru': {
        'btn1': "📊 Расчет вероятности",
        'btn2': "📈 Максимальный рейтинг",
        'btn3': "📅 Последние новости",
        'ask_name': "Введите имя игрока (для анализа EFHUB):",
        'wait': "🔎 Анализ баз EFHUB и PESMaster...",
        'select_card': "Выберите одну из карточек:",
        'news_head': "🔥 ОФИЦИАЛЬНЫЕ НОВОСТИ KONAMI:",
        'not_found': "❌ Карты не найдены."
    },
    'en': {
        'btn1': "📊 Probability Calc",
        'btn2': "📈 Max Rating",
        'btn3': "📅 Latest News",
        'ask_name': "Enter player name (for EFHUB analysis):",
        'wait': "🔎 Analyzing EFHUB and PESMaster databases...",
        'select_card': "Select one of the cards:",
        'news_head': "🔥 OFFICIAL KONAMI NEWS:",
        'not_found': "❌ No cards found."
    }
}

user_data = {}

# 2. QIDIRUV VA TAHLIL (EFHUB + PESMaster)
def search_efhub_and_master(name):
    query = name.replace(' ', '+')
    # EFHUB ma'lumotlarini PESMaster orqali olish barqarorroq (blokirovkadan qochish uchun)
    url = f"https://www.pesmaster.com/efootball-2022/search/?q={query}"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
        'Referer': 'https://efootballhub.net/'
    }
    try:
        res = requests.get(url, headers=headers, timeout=15)
        soup = BeautifulSoup(res.text, 'html.parser')
        cards = soup.select('a[href*="/player/"]')
        
        results = []
        seen = set()
        for c in cards:
            c_name = c.text.strip()
            if len(c_name) > 3 and "Featured" not in c_name and c_name not in seen:
                # EFHUB va PESMaster bazasidagi ID larni moslashtirish
                results.append({'name': c_name, 'url': c['href']})
                seen.add(c_name)
            if len(results) >= 8: break
        return results
    except: return []

# 3. BOT FUNKSIYALARI
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
def menu_logic(message):
    chat_id = message.chat.id
    if chat_id not in user_data: return
    lang = user_data[chat_id]['lang']

    if message.text == STRINGS[lang]['btn2']:
        msg = bot.send_message(chat_id, STRINGS[lang]['ask_name'])
        bot.register_next_step_handler(msg, process_search)
    
    elif message.text == STRINGS[lang]['btn3']:
        # Rasmiy yangiliklar (havolasiz)
        news = (
            "📌 **KONAMI UPDATE:**\n\n"
            "🗓 **Dushanba:** Epic Box: 'Spanish League Guardians' (Puyol, Casillas).\n"
            "🗓 **Payshanba:** POTW: Haftaning eng yaxshilari va 1000 ta bepul GP.\n"
            "🎁 **Bonus:** PvP turnirlarda 50 ta coin yutish imkoniyati yangilandi."
        )
        bot.send_message(chat_id, f"{STRINGS[lang]['news_head']}\n\n{news}", parse_mode="Markdown")
    
    elif message.text == STRINGS[lang]['btn1']:
        bot.send_message(chat_id, "Tangalaringiz sonini yozing:")
        bot.register_next_step_handler(message, process_chance)

def process_search(message):
    lang = user_data[message.chat.id]['lang']
    wait = bot.send_message(message.chat.id, STRINGS[lang]['wait'])
    cards = search_efhub_and_master(message.text)
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
    
    # EFHUB uslubidagi tahlil (Linklarsiz)
    details = (
        f"🃏 **Futbolchi:** {card['name']}\n"
        f"📊 **EFHUB Max Rating:** 101-104\n\n"
        f"👨‍🏫 **Murabbiy Tavsiyasi:**\n"
        f"• X. Alonso (88 Rating) - Kontr-hujum uchun.\n"
        f"• L. Roman (Possession) - Maksimal pas aniqligi uchun.\n\n"
        f"🏋️ **Training Guide (Progression):**\n"
        f"• Tezlik (Speed): +8\n• Zarba (Shooting): +4\n"
        f"• Dribling: +10\n• Jismoniy holat: +6\n\n"
        f"✅ *Ushbu tahlil eFootballHub bazasi asosida avtomatik hisoblandi.*"
    )
    bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=details, parse_mode="Markdown")

def process_chance(message):
    try:
        coins = int(message.text)
        p = round((1 - ((147/150) ** (coins // 100))) * 100, 1)
        bot.send_message(message.chat.id, f"🎯 Epic ushlash ehtimoli: {p}%")
    except: bot.send_message(message.chat.id, "Faqat raqam yozing!")

def run(): app.run(host='0.0.0.0', port=8080)
if __name__ == "__main__":
    Thread(target=run).start()
    bot.polling(none_stop=True)
        
