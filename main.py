import telebot
from telebot import types
import requests
from bs4 import BeautifulSoup
from flask import Flask
from threading import Thread

TOKEN = "8597572815:AAEOgOf8UCmRdoZtHqqkDl-D9Zt0oRRj2LY"
SCRAPER_API_KEY = "75416d669ddf160668872e638d11f605"
bot = telebot.TeleBot(TOKEN)
app = Flask('')

@app.route('/')
def home(): return "Real-time Bot Active"

def get_real_player_data(name):
    search_url = f"https://www.pesmaster.com/efootball-2022/search/?q={name.replace(' ', '+')}"
    proxy_url = f"http://api.scraperapi.com?api_key={SCRAPER_API_KEY}&url={search_url}"
    
    try:
        # 1-qadam: Qidiruv natijasini olish
        res = requests.get(proxy_url, timeout=30)
        soup = BeautifulSoup(res.text, 'html.parser')
        player_link = soup.select_one('.player-card-container a')
        
        if not player_link:
            return "❌ Futbolchi topilmadi. Ismni inglizcha yozing."

        # 2-qadam: Futbolchi sahifasiga kirish
        detail_url = "https://www.pesmaster.com" + player_link['href']
        detail_proxy = f"http://api.scraperapi.com?api_key={SCRAPER_API_KEY}&url={detail_url}"
        
        res_detail = requests.get(detail_proxy, timeout=30)
        soup_detail = BeautifulSoup(res_detail.text, 'html.parser')
        
        # 3-qadam: Haqiqiy ma'lumotlarni qidirish
        real_name = soup_detail.find('h1').text.strip() if soup_detail.find('h1') else name
        # Reytingni aniq klass orqali olish
        rating_tag = soup_detail.select_one('.player-info-main .stat-num')
        real_rating = rating_tag.text.strip() if rating_tag else "Noma'lum"
        
        return (f"✅ **{real_name}**\n\n"
                f"📈 **Haqiqiy Reyting:** {real_rating}\n"
                f"🔗 **Manba:** [Pesmaster]({detail_url})\n\n"
                f"⚙️ **Tavsiya:** Ma'lumotlar saytdan jonli olindi.")
    except Exception as e:
        return "⚠️ Aloqa juda sust. Keyinroq urinib ko'ring."

@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(message.chat.id, "Futbolchi ismini yozing (masalan: Haaland):")

@bot.message_handler(func=lambda m: True)
def handle_msg(message):
    wait = bot.send_message(message.chat.id, "🔎 Sayt ichidan haqiqiy raqamlar qidirilmoqda (20-30 soniya kuting)...")
    result = get_real_player_data(message.text)
    bot.delete_message(message.chat.id, wait.message_id)
    bot.send_message(message.chat.id, result, parse_mode="Markdown")

def run(): app.run(host='0.0.0.0', port=8080)
if __name__ == "__main__":
    Thread(target=run).start()
    bot.polling(none_stop=True)
