from aiogram.fsm.state import State, StatesGroup

class MaxRatingState(StatesGroup):
    player_name = State()
    card_choice = State()
