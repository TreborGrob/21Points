from aiogram.dispatcher.filters.state import State, StatesGroup


class OnlineAction(StatesGroup):
    online_choice = State()
    rating_game = State()
    money_game = State()
    move_player1 = State()
    move_player2 = State()
    result_game = State()


class CommandAction(StatesGroup):
    st_review = State()
