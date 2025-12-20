from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from languages import TEXTS

def main_menu(lang):
    kb = ReplyKeyboardMarkup(resize_keyboard=True)
    kb.add(
        KeyboardButton(TEXTS[lang]["btn_prob"]),
        KeyboardButton(TEXTS[lang]["btn_max"])
    )
    kb.add(KeyboardButton(TEXTS[lang]["btn_news"]))
    return kb
