import random
from aiogram import Bot, Dispatcher, types
from aiogram.dispatcher import FSMContext

from database import select_player, insert_to_db
from game import TOKEN
from aiogram.contrib.fsm_storage.memory import MemoryStorage

from inline_kb import inline_game_km, inline_choose, inline_menu

import asyncio
import logging
import platform
import random
from aiogram import Bot, Dispatcher, types
from aiogram.dispatcher import FSMContext
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from all_states import OnlineAction
from database import insert_to_db, select_player
from inline_kb import inline_game_km, inline_choose, inline_menu, inline_choose2
from operations import issuance_of_card, display_point, card_random

logger = logging.getLogger(__name__)
TOKEN = "5599372356:AAENNx7-DQCXqXUS381lDgVvpEa1GLqeljI"

bot = Bot(token=TOKEN, parse_mode=types.ParseMode.HTML)
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)


@dp.message_handler(commands=['start'], state='*')
async def start(msg: types.Message):
    player = Game()
    await player.reg(msg)


@dp.callback_query_handler(text='yep', state='*')
async def accept(callback: types.CallbackQuery, state: FSMContext):
    player.choice(callback, state)

class Game:
    def __init__(self):
        self.deck = ['6❤', '7❤', '8❤', '9❤', '10❤', 'J❤', 'Q❤', 'K❤', 'A❤', '6♦', '7♦', '8♦', '9♦', '10♦', 'J♦', 'Q♦', 'K♦', 'A♦', '6♣', '7♣', '8♣', '9♣', '10♣', 'J♣', 'Q♣', 'K♣', 'A♣', '6♠', '7♠', '8♠', '9♠', '10♠', 'J♠', 'Q♠', 'K♠', 'A♠']
        self.points = 0
        self.dealer_score = 0
        self.bot = Bot(token=TOKEN, parse_mode=types.ParseMode.HTML)
        self.storage = MemoryStorage()
        self.dp = Dispatcher(self.bot, storage=self.storage)

    async def reg(self, message: types.Message):
        file = open("temp/next-level-card-trick.gif", 'rb')
        await message.answer_animation(animation=file, caption='Сыграем?', reply_markup=inline_game_km)
        player = select_player(message.from_user.id)
        if player:
            pass
        else:
            insert_to_db(id_tg=message.from_user.id, nickname=message.from_user.first_name)

    async def accept(self, callback: types.CallbackQuery):
        await callback.message.delete_reply_markup()
        no_end = "∞"
        await callback.answer('Игра в 21 очко началась')
        await callback.message.answer('Валет - 2 очка, Дама - 3, король - 4.\nТуз может стоить 1 или 11 очков.\n'
                                      f'{no_end:~^21}\n',
                                      reply_markup=inline_choose)

    def card_random(self) -> str:
        random.shuffle(self.deck)
        card = self.deck.pop()
        return card

    def issuance_of_card(self, score: int, card: str) -> int:
        if card.startswith('6'):
            score += 6
        elif card.startswith('7'):
            score += 7
        elif card.startswith('8'):
            score += 8
        elif card.startswith('9'):
            score += 9
        elif card.startswith('10'):
            score += 10
        elif card.startswith('J'):
            score += 2
        elif card.startswith('Q'):
            score += 3
        elif card.startswith('K'):
            score += 4
        elif card.startswith('A'):
            if score <= 10:
                score += 11
            else:
                score += 1
        else:
            score += 10
        return score

    def display_point(self, nick, current, score, robot):
        if not robot:
            return f'{nick} попалась карта {current}, у вас {score} очков.'
        else:
            return f'Дилеру попалась карта {current}, у дилера {score} очков.'

    async def choice(self, callback: types.CallbackQuery, state: FSMContext):
        await callback.message.delete_reply_markup()
        await callback.answer()
        nick = callback.from_user.first_name
        data = await state.get_data()
        if data:
            self.points = int(data.get('points'))
            self.dealer_score = int(data.get('dealer_score'))
            if self.points >= 21 or 21 <= self.dealer_score or self.points >= 19 <= self.dealer_score:
                self.points = 0
                self.dealer_score = 0
        else:
            self.points = 0
            self.dealer_score = 0
            await state.update_data(dealer_score=self.dealer_score, points=self.points)
        print(self.points, '||', self.dealer_score)
        if self.dealer_score < 21 > self.points:
            card = self.card_random()
            card_user = self.card_random()
            points = self.issuance_of_card(self.points, card_user)
            dealer_score = self.issuance_of_card(self.dealer_score, card)
            text_user = self.display_point(nick, card_user, self.points, False)
            text_dealer = self.display_point(nick, card, self.dealer_score, True)
            await callback.message.answer(f'{text_user}\n'
                                          f'{text_dealer}',
                                          reply_markup=inline_choose)
            if self.points > 21 or self.dealer_score == 21:
                await callback.message.answer(f'{nick} проиграл!\n', reply_markup=inline_menu)
                await state.finish()
            elif self.points == 21 == self.dealer_score:
                await callback.message.answer(f'Ничья!\nУ вас {self.points} очков, у дилера {self.dealer_score} очков.',
                                              reply_markup=inline_menu)
                await state.finish()
            elif self.points == 21 or self.dealer_score > 21:
                await callback.message.answer(f'{nick} выиграл! Поздравляем!\n', reply_markup=inline_menu)
                await state.finish()
            elif 21 > self.dealer_score >= 19:
                card_user = self.card_random()
                self.points = self.issuance_of_card(self.points, card_user)
                text_user = self.display_point(nick, card_user, self.points, False)
                await callback.message.answer(f'Дилер оставляет карты, у него {self.dealer_score} очков.\n'
                                              f'{text_user}')
                await state.update_data(dealer_score=self.dealer_score, points=self.points)
                if self.points > 21:
                    await callback.message.answer(f'{nick} проиграл!', reply_markup=inline_menu)
                    await state.finish()
                elif 21 >= self.points > self.dealer_score:
                    await callback.message.answer(f'{nick} одержал победу!', reply_markup=inline_menu)
                    await state.finish()
            await state.update_data(dealer_score=self.dealer_score, points=self.points)
        elif self.points > 21 or self.dealer_score == 21:
            await callback.message.answer(f'{nick} проиграл!\n', reply_markup=inline_menu)
            await state.finish()
        elif self.points == 21 == self.dealer_score:
            await callback.message.answer(f'Ничья!\nУ вас {self.points} очков, у дилера {self.dealer_score} очков.',
                                          reply_markup=inline_menu)
            await state.finish()
        elif self.points == 21 or self.dealer_score > 21:
            await callback.message.answer(f'{nick} выиграл! Поздравляем!\n', reply_markup=inline_menu)
            await state.finish()
        elif 21 > self.dealer_score >= 19:
            card_user = self.card_random()
            self.points = self.issuance_of_card(self.points, card_user)
            text_user = self.display_point(nick, card_user, self.points, False)
            await callback.message.answer(f'Дилер оставляет карты, у него {self.dealer_score} очков.\n'
                                          f'{text_user}')
            if self.points > 21:
                await callback.message.answer(f'{nick} проиграл!', reply_markup=inline_menu)
                await state.finish()
            elif 21 >= self.points > self.dealer_score:
                await callback.message.answer(f'{nick} одержал победу!', reply_markup=inline_menu)
                await state.finish()
        else:
            await callback.message.answer('Нет такого исхода!', reply_markup=inline_menu)
            await state.finish()
