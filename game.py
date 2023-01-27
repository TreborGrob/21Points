import asyncio
import logging
import platform
from aiogram import Bot, Dispatcher, types
from aiogram.dispatcher import FSMContext
from aiogram.contrib.fsm_storage.memory import MemoryStorage

from commands import set_default_commands, register_command
from config import TOKEN
from all_states import OnlineAction
from database import insert_to_db, select_player, update_score, insert_to_rating, select_rating, update_desire, \
    slct_game, update_games_1plr, update_score_rating, update_games_2plr, del_game
from inline_kb import inline_game_km, inline_choose, inline_menu, inline_choose2
from online import connection_game, connect_gamers
from operations import issuance_of_card, display_point, card_random

logger = logging.getLogger(__name__)

bot = Bot(token=TOKEN, parse_mode=types.ParseMode.HTML)
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)


async def on_startup(dispatcher):
    await set_default_commands(dispatcher)


@dp.message_handler(commands=['start'], state='*')
async def reg(message: types.Message):
    file = open("temp/next-level-card-trick.gif", 'rb')
    await message.answer_animation(animation=file, caption='Сыграем?', reply_markup=inline_game_km)
    player = select_player(message.from_user.id)
    if player:
        pass
    else:
        insert_to_db(id_tg=message.from_user.id, nickname=message.from_user.first_name)


@dp.callback_query_handler(text='yep', state='*')
async def accept(callback: types.CallbackQuery):
    await callback.message.delete_reply_markup()
    no_end = "∞"
    await callback.answer('Игра в 21 очко началась')
    await callback.message.answer('Валет - 2 очка, Дама - 3, король - 4.\nТуз может стоить 1 или 11 очков.\n'
                                  f'{no_end:~^21}\n',
                                  reply_markup=inline_choose)


@dp.callback_query_handler(text='plus', state='*')
# @dp.message_handler(commands=["game"], state="*")
async def choice(callback: types.CallbackQuery, state: FSMContext):
    try:
        info_player = select_player(callback.from_user.id)
        games = info_player[0]
        wins = info_player[1]
        loses = info_player[2]
        draws = info_player[3]
    except Exception as e:
        logger.info(e)
        insert_to_db(id_tg=callback.from_user.id, nickname=callback.from_user.first_name)
        games = 0
        wins = 0
        loses = 0
        draws = 0
    await callback.message.delete_reply_markup()
    await callback.answer()
    id_gamer = callback.from_user.id
    nick = callback.from_user.first_name
    try:
        data = await state.get_data()
        points = int(data.get('points'))
        dealer_score = int(data.get('dealer_score'))
    except TypeError:
        points = 0
        dealer_score = 0

    if 19 <= points == dealer_score <= 21:
        await callback.message.answer(f'⚖Ничья!\nУ вас {points} очков, у дилера {dealer_score} очков.',
                                      reply_markup=inline_menu)
        await state.finish()
        update_score(id_gamer, games+1, wins, loses, draws+1, 'draw')
    elif points > 21 or dealer_score == 21:
        await callback.message.answer(f'🏳{nick} проиграл!\n', reply_markup=inline_menu)
        await state.finish()
        update_score(id_gamer, games+1, wins, loses+1, draws, 'lose')
    elif points == 21 or dealer_score > 21:
        await callback.message.answer(f'🥇{nick} выиграл! Поздравляем!\n', reply_markup=inline_menu)
        await state.finish()
        update_score(id_gamer, games+1, wins+1, loses, draws)
    elif 21 > dealer_score >= 19 > points:
        card_user = card_random()
        points = issuance_of_card(points, card_user)
        text_user = display_point(nick, card_user, points, False)
        await callback.message.answer(f'🏁Дилер оставляет карты, у него {dealer_score} очков.\n'
                                      f'{text_user}', reply_markup=inline_menu)
        await state.update_data(points=points)
        if 19 <= points == dealer_score <= 21:
            await callback.message.answer(f'⚖Ничья!\nУ вас {points} очков, у дилера {dealer_score} очков.',
                                          reply_markup=inline_menu)
            await state.finish()
            update_score(id_gamer, games+1, wins, loses, draws+1, 'draw')
        elif points > 21:
            await callback.message.answer(f'🏳{nick} проиграл!', reply_markup=inline_menu)
            await state.finish()
            update_score(id_gamer, games+1, wins, loses+1, draws, 'lose')
        elif 21 >= points > dealer_score:
            await callback.message.answer(f'🥇{nick} одержал победу!', reply_markup=inline_menu)
            await state.finish()
            update_score(id_gamer, games+1, wins+1, loses, draws)
    elif dealer_score < 21 > points:
        card = card_random()
        card_user = card_random()
        points = issuance_of_card(points, card_user)
        dealer_score = issuance_of_card(dealer_score, card)
        text_user = display_point(nick, card_user, points, False)
        text_dealer = display_point(nick, card, dealer_score, True)
        await callback.message.answer(f'{text_user}\n'
                                      f'{text_dealer}',
                                      reply_markup=inline_choose)
        await state.update_data(dealer_score=dealer_score, points=points)
        if 19 <= points == dealer_score <= 21:
            await callback.message.answer(f'⚖Ничья!\nУ вас {points} очков, у дилера {dealer_score} очков.',
                                          reply_markup=inline_menu)
            await state.finish()
            update_score(id_gamer, games+1, wins, loses, draws+1, 'draw')
        elif points > 21 or dealer_score == 21:
            await callback.message.answer(f'🏳{nick} проиграл!\n', reply_markup=inline_menu)
            await state.finish()
            update_score(id_gamer, games+1, wins, loses+1, draws, 'lose')
        elif points == 21 or dealer_score > 21:
            await callback.message.answer(f'🥇{nick} выиграл! Поздравляем!\n', reply_markup=inline_menu)
            await state.finish()
            update_score(id_gamer, games+1, wins+1, loses, draws)

    else:
        await callback.message.answer('Нет такого исхода!', reply_markup=inline_menu)
        await state.finish()


@dp.callback_query_handler(text='minus', state='*')
async def choice_m(callback: types.CallbackQuery, state: FSMContext):
    info_player = select_player(callback.from_user.id)
    games = info_player[0]
    wins = info_player[1]
    loses = info_player[2]
    draws = info_player[3]
    id_gamer = callback.from_user.id
    await callback.answer()
    data = await state.get_data()
    if data:
        points = int(data.get('points'))
        dealer_score = int(data.get('dealer_score'))
    else:
        points = 0
        dealer_score = 0
    if dealer_score > points:
        await callback.message.answer(f'🏳Вы проиграли!\nУ вас {points} очков, у дилера {dealer_score} очков',
                                      reply_markup=inline_choose)
        await state.finish()
        update_score(id_gamer, games+1, wins, loses+1, draws, 'lose')
    elif points > dealer_score and dealer_score < 19:
        while dealer_score < 19:
            if 18 < dealer_score < 21 and dealer_score > points:
                await callback.message.answer(f'🏳Вы проиграли, у вас {points} очков, у дилера {dealer_score} очков',
                                              reply_markup=inline_choose)
                await state.finish()
                update_score(id_gamer, games+1, wins, loses+1, draws, 'lose')
                break
            elif points == dealer_score == 21:
                await callback.message.answer(f'⚖Ничья!\nУ вас {points} очков, у дилера {dealer_score} очков.',
                                              reply_markup=inline_menu)
                await state.finish()
                update_score(id_gamer, games+1, wins, loses, draws+1, 'draw')
                break
            elif dealer_score > 21:
                await callback.message.answer(f'🥇Вы победили, у вас {points} очков, у дилера {dealer_score} очков',
                                              reply_markup=inline_choose)
                await state.finish()
                update_score(id_gamer, games+1, wins+1, loses, draws)
                break
            else:
                card = card_random()
                dealer_score = issuance_of_card(dealer_score, card)
                await state.update_data(dealer_score=dealer_score)
                if 18 < dealer_score <= 21 and dealer_score > points:
                    text_dealer = f'Дилеру выпала карта {card}.\n🏳Вы проиграли, у вас {points} очков, ' \
                                  f'у дилера {dealer_score} очков'
                    await callback.message.answer(text_dealer, reply_markup=inline_choose)
                    await state.finish()
                    update_score(id_gamer, games+1, wins, loses+1, draws, 'lose')
                elif points == dealer_score <= 21:
                    text_dealer = f'Дилеру выпала карта {card}.\n⚖Ничья!\nУ вас {points} очков, ' \
                                  f'у дилера {dealer_score} очков.'
                    await callback.message.answer(text_dealer, reply_markup=inline_choose)
                    await state.finish()
                    update_score(id_gamer, games+1, wins, loses, draws+1, 'draw')
                    break
                elif dealer_score > 21:
                    text_dealer = f'Дилеру попалась карта {card}.\n' \
                                  f'🥇Вы победили, у вас {points} очков, у дилера {dealer_score} очков'
                    await callback.message.answer(text_dealer, reply_markup=inline_choose)
                    await state.finish()
                    update_score(id_gamer, games+1, wins+1, loses, draws)
                else:
                    if 18 < dealer_score <= 21 and dealer_score > points:
                        text_dealer = f'Дилеру выпала карта {card}.\n🏳Вы проиграли, у вас {points} очков, ' \
                                      f'у дилера {dealer_score} очков'
                        await callback.message.answer(text_dealer, reply_markup=inline_choose)
                        await state.finish()
                        update_score(id_gamer, games+1, wins, loses+1, draws, 'lose')

                    elif points == dealer_score <= 21:
                        text_dealer = f'Дилеру выпала карта {card}.\n⚖Ничья!\nУ вас {points} очков, ' \
                                      f'у дилера {dealer_score} очков.'
                        await callback.message.answer(text_dealer, reply_markup=inline_choose)
                        await state.finish()
                        update_score(id_gamer, games+1, wins, loses, draws+1, 'draw')

                    elif dealer_score > 21:
                        text_dealer = f'Дилеру выпала карта {card}.\n🥇Вы победили, у вас {points} очков, ' \
                                      f'у дилера {dealer_score} очков'
                        await callback.message.answer(text_dealer, reply_markup=inline_choose)
                        await state.finish()
                        update_score(id_gamer, games+1, wins+1, loses, draws)

                    else:
                        text_dealer = display_point(callback.from_user.first_name, card, dealer_score, True)
                        await callback.message.answer(text_dealer, reply_markup=inline_choose)
                        await state.finish()


@dp.callback_query_handler(text='nope', state='*')
async def no_accept(callback: types.CallbackQuery, state: FSMContext):
    await callback.message.delete()
    await state.reset_state()


@dp.callback_query_handler(text='start', state='*')
async def menu(callback: types.CallbackQuery, state: FSMContext):
    await callback.message.delete_reply_markup()
    text = 'Меню'
    # file = open("temp/outerspace-58.gif", 'rb')
    # await callback.message.answer_animation(animation=file, caption=f"{text:~^20}", reply_markup=inline_menu)
    await callback.message.answer(f"{text:~^20}", reply_markup=inline_menu)
    await state.reset_state()


@dp.callback_query_handler(text='online_game')
async def online_game(callback: types.CallbackQuery, state: FSMContext):
    player1 = callback.from_user.id
    existence = select_rating(player1)
    if not existence:
        insert_to_rating(id_tg=player1, nickname=callback.from_user.first_name)
    await callback.answer('Подбор игроков...🎲')
    update_desire(player1, True)
    player1_score = 0
    player2_score = 0
    connect_gamers(player1)
    game = slct_game(player1)
    print(game)
    if game:
        if game[0][1] != player1:
            player2 = game[0][1]
        else:
            player2 = game[0][2]
        await connection_game(bot, player1, player2)
        await OnlineAction.online_choice.set()
        await state.update_data(pl1=player1_score, pl2=player2_score, player1=player1, player2=player2)
    else:
        print('Game not found!')


@dp.callback_query_handler(text='result', state='*')
# @dp.message_handler(commands=["stats"], state="*")
async def stats(callback: types.CallbackQuery):
    await callback.answer()
    try:
        data = select_player(callback.from_user.id)
        games = data[0]
        wins = data[1]
        loses = data[2]
        draws = data[3]
        winrait = (wins + 0.5 * draws) / games * 100
        await callback.message.answer(f'🔁 Всего игр : {games}\n'
                                      f'🏅 Побед : {wins}\n'
                                      f'⚰ Поражений : {loses}\n'
                                      f'🛡 Ничьи : {draws}\n'
                                      f'📊 Винрейт : {round(winrait, 2)}%')
    except Exception as e:
        await callback.message.answer(f'Нет результата, старайся лучше!')
        logger.error(f'Not found player!\n{e}')


@dp.callback_query_handler(text="plus_multy", state=OnlineAction.online_choice)
async def plus_multy(callback: types.CallbackQuery):
    await callback.message.delete_reply_markup()
    await callback.answer('Wait...')
    game = slct_game(callback.from_user.id)
    if game:
        print(game)
        all_dict = {'id_game': game[0][0],
                    'id_tg_player_one': game[0][1],
                    'id_tg_player_two': game[0][2],
                    'status': game[0][3],
                    'result': game[0][4],
                    'score_one': game[0][5],
                    'score_two': game[0][6],
                    'move_one': game[0][7],
                    'move_two': game[0][8],
                    }
        if all_dict['id_tg_player_one'] == callback.from_user.id:
            player1_score = int(all_dict['score_one'])
            player2_score = int(all_dict['score_two'])
            player2_id = int(all_dict['id_tg_player_two'])

            if player1_score > 21 >= player2_score:
                await callback.message.answer('Ты проиграл(а)!')
                update_score_rating(all_dict['id_tg_player_one'], 'lose')
                await bot.send_message(player2_id, 'Ты победил(а)!')
                update_score_rating(player2_id)
                del_game(int(all_dict['id_game']))
            elif player1_score == 21 < player2_score:
                await callback.message.answer('Ты выиграл(а)!')
                update_score_rating(all_dict['id_tg_player_one'])
                await bot.send_message(player2_id, 'You lose!')
                update_score_rating(player2_id, 'lose')
                del_game(int(all_dict['id_game']))
            elif player1_score < 21 > player2_score:
                gamer = callback.from_user.username
                card = card_random()
                player1_score = issuance_of_card(player1_score, card)
                update_games_1plr(player1_score, False, all_dict['id_game'])
                text = f'{gamer} получил карту {card}, у него {player1_score} очков!'
                await callback.message.answer(text, reply_markup=inline_choose2)
                await bot.send_message(player2_id, text)
                # await OnlineAction.online_choice.set()
        else:
            player2_id = int(all_dict['id_tg_player_one'])
            player1_score = int(all_dict['score_two'])
            player2_score = int(all_dict['score_one'])
            if player1_score > 21 >= player2_score:
                await callback.message.answer('Ты проиграл(а)!')
                update_score_rating(int(all_dict['id_tg_player_two']), 'lose')
                await bot.send_message(player2_id, 'Ты победил(а)!')
                update_score_rating(player2_id)
                del_game(int(all_dict['id_game']))
            elif player1_score == 21 < player2_score:
                await callback.message.answer('Ты выиграл(а)!')
                update_score_rating(all_dict['id_tg_player_two'])
                await bot.send_message(player2_id, 'You lose!')
                update_score_rating(player2_id, 'lose')
                del_game(int(all_dict['id_game']))
            elif player1_score < 21 > player2_score:
                gamer = callback.from_user.username
                card = card_random()
                player1_score = issuance_of_card(player1_score, card)
                update_games_2plr(player1_score, False, all_dict['id_game'])
                text = f'{gamer} получил карту {card}, у него {player1_score} очков!'
                await callback.message.answer(text, reply_markup=inline_choose2)
                await bot.send_message(player2_id, text)
                # await OnlineAction.online_choice.set()


async def main():
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(name)s - %(message)s",
    )
    logger.error("Starting bot")
    await on_startup(dp)
    register_command(dp)
    try:
        await dp.start_polling()

    finally:
        await dp.storage.close()
        await dp.storage.wait_closed()
        await bot.session.close()


if __name__ == "__main__":
    try:
        if platform.system() == 'Windows':
            asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        logger.error("Bot stopped!")
