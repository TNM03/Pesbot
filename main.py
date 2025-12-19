import telebot
import sqlite3
import math
import time
from telebot import types

TOKEN = "8395823915:AAEf14qC8fw_IooY3Nabfvt_g0zssJ3xjxc"
bot = telebot.TeleBot(TOKEN)

# Bazani kengaytiramiz: yutuqlar jadvalini qo'shamiz
def init_db():
    conn = sqlite3.connect('efootball_v3.db')
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS users 
                      (id INTEGER PRIMARY KEY, coins INTEGER)''')
    cursor.execute('''CREATE TABLE IF NOT EXISTS wins 
                      (user_id INTEGER, win_time INTEGER)''')
    conn.commit()
    conn.close()

# Asosiy menyu tugmalari
def main_menu():
    markup = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    btn1 = types.KeyboardButton("💰 Balansni yangilash")
    btn2 = types.KeyboardButton("📊 Tahlil va Maslahat")
    btn3 = types.KeyboardButton("🔥 Menga EPIC tushdi!")
    btn4 = types.KeyboardButton("📉 Live Omad Grafigi")
    markup.add(btn1, btn2, btn3, btn4)
    return markup

@bot.message_handler(commands=['start'])
def start(message):
    init_db()
    bot.reply_to(message, "⚽ **eFootball Jamoaviy Tahlil Markazi**\n\nMenyudan kerakli bo'limni tanlang:", 
                 reply_markup=main_menu())

@bot.message_handler(func=lambda message: message.text == "💰 Balansni yangilash")
def ask_coins(message):
    msg = bot.send_message(message.chat.id, "Hozirgi tangalaringiz miqdorini yozing:")
    bot.register_next_step_handler(msg, save_coins)

def save_coins(message):
    if message.text.isdigit():
        conn = sqlite3.connect('efootball_v3.db')
        cursor = conn.cursor()
        cursor.execute("INSERT OR REPLACE INTO users (id, coins) VALUES (?, ?)", 
                       (message.chat.id, int(message.text)))
        conn.commit()
        conn.close()
        bot.send_message(message.chat.id, "✅ Balans saqlandi!", reply_markup=main_menu())
    else:
        bot.send_message(message.chat.id, "❌ Faqat raqam yozing.")

@bot.message_handler(func=lambda message: message.text == "🔥 Menga EPIC tushdi!")
def report_win(message):
    conn = sqlite3.connect('efootball_v3.db')
    cursor = conn.cursor()
    current_time = int(time.time())
    cursor.execute("INSERT INTO wins (user_id, win_time) VALUES (?, ?)", 
                   (message.chat.id, current_time))
    conn.commit()
    conn.close()
    bot.send_message(message.chat.id, "🎉 Tabriklaymiz! Sizning muvaffaqiyatingiz jamoaviy tahlilga qo'shildi. Boshqalarga ham yordamingiz tegadi!")

@bot.message_handler(func=lambda message: message.text == "📉 Live Omad Grafigi")
def live_analysis(message):
    conn = sqlite3.connect('efootball_v3.db')
    cursor = conn.cursor()
    fifteen_mins_ago = int(time.time()) - 900 # 15 daqiqa
    cursor.execute("SELECT COUNT(*) FROM wins WHERE win_time > ?", (fifteen_mins_ago,))
    count = cursor.fetchone()[0]
    conn.close()
    
    status = "TINCH"
    advice = "Hozircha serverda yirik yutuqlar kam. Kutish tavsiya etiladi."
    if count >= 3:
        status = "QIZIQARLI"
        advice = "Yutuqlar soni ortmoqda. Kichik urinish qilib ko'ring!"
    if count >= 7:
        status = "🔥 JUDA QIZIQ!"
        advice = "Hozir omadli vaqt! Server ko'p Epic bermoqda. Pack oching!"

    bot.send_message(message.chat.id, f"📡 **Live Holat:** {status}\n"
                                     f"📈 Oxirgi 15 daqiqada tushgan Epiclar: {count} ta\n"
  import os
from flask import Flask
from threading import Thread

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
    keep_alive()  # Botni uyquga ketishdan asraydi
    # Bu yerda init_db() funksiyasi kodingizda borligini tekshiring
    print("Bot muvaffaqiyatli ishga tushdi...")
    bot.polling(none_stop=True)
                                   f"💡 **Maslahat:** {advice}")

