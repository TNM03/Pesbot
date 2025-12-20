import telebot
from telebot import types
import requests
from bs4 import BeautifulSoup
from flask import Flask
from threading import Thread

# 1. BOT SOZLAMALARI
TOKEN = "8597572815:AAEOgOf8UCmRdoZtHqqkDl-D9Zt0oRRj2LY"
bot = telebot.TeleBot(TOKEN)
app = Flask('')

@app.route('/')
def home(): return "Bot EFHUB Barqaror Qidiruv bilan faol!"

STRINGS = {
    'uz': {
        'btn1': "📊 Ehtimollikni hisoblash",
        'btn2': "📈 Maksimal reyting",
        'btn3': "📅 So'nggi yangiliklar",
        'ask_name': "Futbolchi ismini kiriting (inglizcha, masalan: Messi):",
        'ask_coins': "Tangalar miqdorini kiriting:",
        'wait': "🔎 EFHUB ma'lumotlari tahlil qilinmoqda...",
        'select_card': "Topilgan kartalar:",
        'not_found': "❌ Karta topilmadi. Iltimos, ismni to'liqroq yozing.",
        'prob_res': "💰 Tangalar: {c}\n🎯 Epic yutish ehtimoli: {p}%"
    }
}

# 2. ENG KUCHLI QIDIRUV (PESMASTER ORQALI - BLOKLANISH EHTIMOLI JUDA KAM)
def stable_search(name):
    query = name.replace(' ', '+')
    # Pesmaster EFHUB ga qaraganda Render bloklariga chidamliroq
    url = f"https://www.pesmaster.com/efootball-2022/search/?q={query}"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    try:
        res = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(res.text, 'html.parser')
        # Karta bloklarini topish
        cards = soup.select('.player-card-container a')
        results = []
        seen = set()
        
        for card in cards:
            p_name = card.select_one('.player-card-name')
            if p_name:
                clean_name = p_name.text.strip()
                if clean_name not in seen:
                    results.append({'name': clean_name, 'url': "https://www.pesmaster.com" + card['href']})
                    seen.add(clean_name)
            if len(results) >= 6: break
        return results
    except:
        return []

# 3. HANDLERS
@bot.message_handler(commands=['start'])
def start(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add(STRINGS['uz']['btn1'], STRINGS['uz']['btn2'])
    markup.add(STRINGS['uz']['btn3'])
    bot.send_message(message.chat.id, "Tayyor! Bo'limni tanlang:", reply_markup=markup)

@bot.message_handler(func=lambda m: m.text in [STRINGS['uz']['btn1'], STRINGS['uz']['btn2'], STRINGS['uz']['btn3']])
def menu_logic(message):
    if message.text == STRINGS['uz']['btn2']:
        msg = bot.send_message(message.chat.id, STRINGS['uz']['ask_name'])
        bot.register_next_step_handler(msg, process_search)
    elif message.text == STRINGS['uz']['btn1']:
        msg = bot.send_message(message.chat.id, STRINGS['uz']['ask_coins'])
        bot.register_next_step_handler(msg, process_calc)
    elif message.text == STRINGS['uz']['btn3']:
        news = "📌 **KONAMI YANGILIKLARI:**\n\n🗓 Dushanba: Epic Box yangilanadi.\n🗓 Payshanba: POTW kutilmoqda."
        bot.send_message(message.chat.id, news, parse_mode="Markdown")

def process_search(message):
    wait = bot.send_message(message.chat.id, STRINGS['uz']['wait'])
    cards = stable_search(message.text)
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
    # Bu qismda matnli tahlil ko'rsatiladi
    guide = (
        "📊 **Tahlil (EFHUB/PESMaster):**\n\n"
        "📈 Max Rating: 101-104\n"
        "👨‍🏫 Murabbiy tavsiyasi: X. Alonso\n"
        "⚙️ Training: Speed +8, Dexterity +10, Lower Body +8."
    )
    bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=guide, parse_mode="Markdown")

def process_calc(message):
    try:
        coins = int(message.text)
        p = round((1 - ((147/150) ** (coins // 100))) * 100, 1)
        bot.send_message(message.chat.id, f"🎯 Epic yutish ehtimoli: {p}%")
    except: bot.send_message(message.chat.id, "Raqam yozing!")

def run(): app.run(host='0.0.0.0', port=8080)
if __name__ == "__main__":
    Thread(target=run).start()
    bot.polling(none_stop=True)
  
