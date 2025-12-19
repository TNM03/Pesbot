import telebot
import sqlite3
import time
import os
from flask import Flask
from threading import Thread

# Bot tokeningizni shu yerga yozing
TOKEN = "8597572815:AAEOgOf8UCmRdoZtHqqkDl-D9Zt0oRRj2LY"
bot = telebot.TeleBot(TOKEN)

# Ma'lumotlar bazasini sozlash
def init_db():
    conn = sqlite3.connect('efootball_v3.db')
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS wins 
                      (user_id INTEGER, chat_id INTEGER, timestamp INTEGER)''')
    conn.commit()
    conn.close()

@bot.message_handler(commands=['start'])
def send_welcome(message):
    # Tugmalarni yaratish
    markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
    btn1 = telebot.types.KeyboardButton("📊 Tahlil")
    markup.add(btn1)
    
    bot.reply_to(message, "Assalomu alaykum! Pesbot v3 ishga tushdi. Quyidagi tugmani bosing:", reply_markup=markup)

# Tugma bosilganda ishlaydigan qism
@bot.message_handler(func=lambda message: message.text == "📊 Tahlil")
def tahlil_button(message):
    live_analysis(message)

@bot.message_handler(commands=['tahlil'])
def live_analysis(message):
    conn = sqlite3.connect('efootball_v3.db')
    cursor = conn.cursor()
    fifteen_mins_ago = int(time.time()) - 900
    cursor.execute("SELECT COUNT(*) FROM wins WHERE timestamp > ?", (fifteen_mins_ago,))
    count = cursor.fetchone()[0]
    conn.close()

    status = "TINCH"
    advice = "Hozircha serverda yirik yutuqlar kam."
    
    if count >= 3:
        status = "QIZIQARLI"
        advice = "Yutuqlar soni ortmoqda. Kichik stavkalar qilish mumkin."
    if count >= 7:
        status = "🔥 JUDA QIZIQ!"
        advice = "Hozir omadli vaqt! Server yutuq beryapti."

    response = (
        f"📊 **Vaziyat:** {status}\n"
        f"📈 Oxirgi 15 daqiqadagi yutuqlar: {count}\n"
        f"💡 **Maslahat:** {advice}"
    )
    bot.send_message(message.chat.id, response, parse_mode="Markdown")

# Render uchun "Keep Alive" qismi
app = Flask('')

@app.route('/')
def home():
    return "Bot is running!"

def run():
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 8080)))

def keep_alive():
    t = Thread(target=run)
    t.start()

if __name__ == "__main__":
    init_db()
    keep_alive()
    print("Bot muvaffaqiyatli ishga tushdi...")
    bot.polling(none_stop=True)
