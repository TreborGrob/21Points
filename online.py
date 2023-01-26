import random
from mysql.connector import Error, connect
from database import wait_gamers, update_desire, add_in_game
from aiogram import types, Bot
from inline_kb import inline_choose2

TOKEN = "5599372356:AAENNx7-DQCXqXUS381lDgVvpEa1GLqeljI"
bot = Bot(token=TOKEN, parse_mode=types.ParseMode.HTML)


def connect_gamers(player_one: int):
    all_gamers = wait_gamers()
    if all_gamers:
        all_gamers = [item for sublist in all_gamers for item in sublist]
        print('Все игроки : ', all_gamers)
        if len(all_gamers) >= 2:
            random.shuffle(all_gamers)
            player_two = all_gamers.pop()
            if player_one != player_two:
                add_in_game(tg_id_one=player_one, tg_id_two=player_two, status=True,
                            result='play', score_one=0, score_two=0)
                print('Add game.')
                update_desire(player_one, False)
                update_desire(player_two, False)
            else:
                connect_gamers(player_one)
            #     print('Not fart')


async def connection_game(robot, plr1, plr2):
    text = 'Игра началась!'
    await robot.send_message(chat_id=plr1, text=text, reply_markup=inline_choose2)
    await robot.send_message(chat_id=plr2, text=text, reply_markup=inline_choose2)


if __name__ == '__main__':
    try:
        with connect(
                host="localhost",
                user="pointstwoone",
                password="vlowkz3O!",
        ) as connection:
            create_db_query = "CREATE DATABASE online_points"
            with connection.cursor() as cursor:
                cursor.execute(create_db_query)
    except Error as e:
        print(e)
