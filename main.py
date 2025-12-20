import telebot
from telebot import types

# BOT TOKENINGIZ
TOKEN = "8597572815:AAEOgOf8UCmRdoZtHqqkDl-D9Zt0oRRj2LY"
bot = telebot.TeleBot(TOKEN)

@bot.message_handler(commands=['start'])
def start(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add("📈 Maksimal reytingni ko'rish")
    bot.send_message(message.chat.id, "Salom! Futbolchi ismini yozsangiz, uning EFHUB linkini beraman.", reply_markup=markup)

@bot.message_handler(func=lambda m: True)
def handle_text(message):
    if message.text == "📈 Maksimal reytingni ko'rish":
        bot.send_message(message.chat.id, "Futbolchi ismini inglizcha yozing (masalan: Messi):")
    else:
        # Saytning o'zida qidiruv havolasini yasash
        player_name = message.text.replace(' ', '+')
        link = f"https://efootballhub.net/efootball23/search/players?searchQuery={player_name}"
        
        text = (
            f"🔍 **{message.text}** uchun qidiruv natijasi:\n\n"
            f"Pastdagi havola orqali futbolchining barcha stats va maksimal reytingini ko'rishingiz mumkin 👇"
        )
        
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton("🌐 EFHUB'da ko'rish", url=link))
        bot.send_message(message.chat.id, text, reply_markup=markup, parse_mode="Markdown")

if __name__ == "__main__":
    bot.polling(none_stop=True)
