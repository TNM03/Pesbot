import telebot
import random

TOKEN = "8597572815:AAEOgOf8UCmRdoZtHqqkDl-D9Zt0oRRj2LY"
bot = telebot.TeleBot(TOKEN)

# Botning "Miyasi" - Ma'lumotlar bazasi
PLAYER_DB = {
    "messi": {"name": "Lionel Messi", "rating": "102-105", "style": "Creative Playmaker", "boost": "Dribbling +10, Tight turns +8"},
    "ronaldo": {"name": "Cristiano Ronaldo", "rating": "101-103", "style": "Goal Poacher", "boost": "Finishing +12, Heading +8"},
    "mbappe": {"name": "Kylian Mbappé", "rating": "102-104", "style": "Goal Poacher", "boost": "Speed +10, Acceleration +12"},
    "neymar": {"name": "Neymar Jr", "rating": "101-103", "style": "Creative Playmaker", "boost": "Ball Control +10, Dexterity +9"},
    "haaland": {"name": "Erling Haaland", "rating": "100-103", "style": "Goal Poacher", "boost": "Physical Contact +12, Finishing +10"},
    "vinicius": {"name": "Vinícius Júnior", "rating": "100-102", "style": "Roaming Flank", "boost": "Speed +11, Dribbling +9"}
}

def analyze_logic(name):
    name_lower = name.lower()
    
    # Bazadan qidirish
    if name_lower in PLAYER_DB:
        p = PLAYER_DB[name_lower]
        return (f"👤 **Tahlilchi javobi:**\n\n"
                f"Men **{p['name']}** kartasini o'rganib chiqdim. U hozirgi metada juda kuchli! ✅\n\n"
                f"📊 **Reyting:** {p['rating']}\n"
                f"🎭 **O'yin uslubi:** {p['style']}\n"
                f"⚙️ **Tavsiya:** {p['boost']}.\n\n"
                f"Sizga ushbu futbolchini tarkibda saqlashni maslahat beraman.")
    
    # Agar bazada bo'lmasa, "aqlli" umumiy tahlil
    else:
        return (f"🧐 **Tahlil:**\n\n"
                f"**{name}** haqida ma'lumotlarimni yangilayapman. Taxminimcha, uning maksimal reytingi **98-101** atrofida. "
                f"Unga ko'proq 'Speed' va 'Stamina' berishni tavsiya qilaman. 📈")

@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(message.chat.id, "Assalomu alaykum! Men eFootball tahlilchisiman. Futbolchi ismini yozing:")

@bot.message_handler(func=lambda m: True)
def handle_msg(message):
    # Xuddi odamdek "yozmoqda..." holati
    bot.send_chat_action(message.chat.id, 'typing') 
    import time
    time.sleep(2) # "O'ylash" effekti
    
    response = analyze_logic(message.text)
    bot.reply_to(message, response, parse_mode="Markdown")

bot.polling()

