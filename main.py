
import telebot
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
def home(): return "Bot Active"

def get_clean_data(player_name):
    # Pesmaster qidiruv sahifasi
    search_url = f"https://www.pesmaster.com/efootball-2022/search/?q={player_name.replace(' ', '+')}"
    proxy_url = f"http://api.scraperapi.com?api_key={SCRAPER_API_KEY}&url={search_url}"
    
    try:
        res = requests.get(proxy_url, timeout=30)
        soup = BeautifulSoup(res.text, 'html.parser')
        player_card = soup.select_one('.player-card-container a')
        
        if not player_card:
            return "❌ Kechirasiz, bunday futbolchi topilmadi."

        # Futbolchi sahifasiga kirib, raqamlarni olish
        detail_url = "https://www.pesmaster.com" + player_card['href']
        detail_proxy = f"http://api.scraperapi.com?api_key={SCRAPER_API_KEY}&url={detail_url}"
        
        res_detail = requests.get(detail_proxy, timeout=30)
        soup_detail = BeautifulSoup(res_detail.text, 'html.parser')
        
        # Ma'lumotlarni tozalash (Linksiz)
        name = soup_detail.find('h1').text.strip()
        rating = soup_detail.select_one('.player-info-main .stat-num').text.strip()
        
        # Chiroyli tahlil matni
        response_text = (
            f"👤 **Futbolchi:** {name}\n"
            f"📈 **Maksimal reyting:** {rating}\n\n"
            f"📊 **Tahlil:**\n"
            f"Ushbu futbolchi o'z pozitsiyasida juda samarali. "
            f"Maksimal darajaga yetkazish uchun Speed va Dexterity ko'rsatkichlariga e'tibor bering."
        )
        return response_text
    except:
        return "⚠️ Ma'lumot olishda xatolik yuz berdi. Birozdan so'ng qayta urinib ko'ring."

@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(message.chat.id, "Futbolchi ismini kiriting (masalan: Mbappe):")

@bot.message_handler(func=lambda m: True)
def handle_msg(message):
    wait = bot.send_message(message.chat.id, "🔎 Tahlil qilinmoqda...")
    result = get_clean_data(message.text)
    bot.delete_message(message.chat.id, wait.message_id)
    bot.send_message(message.chat.id, result, parse_mode="Markdown")

def run(): app.run(host='0.0.0.0', port=8080)
if __name__ == "__main__":
    Thread(target=run).start()
    bot.polling(none_stop=True)
