from aiogram import Bot, Dispatcher, F
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from aiogram.filters import Command
import asyncio

from config import BOT_TOKEN, DEFAULT_LANG
from keyboards import main_menu
from languages import TEXTS
from states import MaxRatingState
from services.efootballhub_parser import get_player_cards
from services.rating_logic import get_max_rating_recommendations
from services.news_provider import get_latest_news

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

USER_LANG = {}

@dp.message(Command("start"))
async def start(msg: Message):
    USER_LANG[msg.from_user.id] = DEFAULT_LANG
    await msg.answer(
        TEXTS[DEFAULT_LANG]["menu"],
        reply_markup=main_menu(DEFAULT_LANG)
    )

@dp.message(F.text.contains("Maksimal") | F.text.contains("Maximum") | F.text.contains("Максим"))
async def max_rating_start(msg: Message, state: FSMContext):
    await msg.answer("Futbolchi nomini kiriting:")
    await state.set_state(MaxRatingState.player_name)

@dp.message(MaxRatingState.player_name)
async def get_cards(msg: Message, state: FSMContext):
    cards = get_player_cards(msg.text)
    await state.update_data(player=msg.text)

    text = "Kartani tanlang:\n"
    for i, c in enumerate(cards, 1):
        text += f"{i}. {c}\n"

    await msg.answer(text)
    await state.set_state(MaxRatingState.card_choice)

@dp.message(MaxRatingState.card_choice)
async def give_recommendations(msg: Message, state: FSMContext):
    recs = get_max_rating_recommendations(msg.text)
    result = "📈 Maksimal reyting uchun:\n\n"

    for r in recs:
        result += f"👤 Murabbiy: {r['coach']}\n"
        result += f"🏋️ Training: {r['training']}\n\n"

    await msg.answer(result)
    await state.clear()

@dp.message(F.text.contains("yangilik") | F.text.contains("news") | F.text.contains("нов"))
async def news(msg: Message):
    news_list = get_latest_news()
    await msg.answer("\n\n".join(news_list))

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
