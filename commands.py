from aiogram import Dispatcher, types, Bot
from aiogram.dispatcher import FSMContext
from config import TOKEN, ADMIN_ID
from all_states import CommandAction

bot = Bot(token=TOKEN, parse_mode=types.ParseMode.HTML)


async def set_default_commands(dp):
    await dp.bot.set_my_commands(
        [
            types.BotCommand("start", "Начать игру"),
            # types.BotCommand("game", "Играть/продолжить игру"),
            # types.BotCommand("stats", "Статистика"),
            types.BotCommand("help", "Правила игры"),
            types.BotCommand("review", "Написать отзыв | предложение"),

        ]
    )


async def help_command(message: types.Message):
    await message.answer('<b>Правила игры:</b>\n'
                         'Для победы необходимо набрать 21 очко\n'
                         'Либо чтобы соперник набрал больше 21 очка (т.н. перебор)\n'
                         'Значение Туза = 11, если у вас меньше 10 очков, либо 1 очко, если грозит перебор\n'
                         'Король - 4, Дама - 3, Валет - 2\n'
                         'Остальные карты по номиналу\n'
                         'В раздаче участвуют несколько колод, не пытайтесь просчитать😜')


async def comment(message: types.Message):
    await message.answer('Напишите ваш отзыв или предложение.\n'
                         'Ваше мнение очень важно для нас!\n')
    await CommandAction.st_review.set()


async def comment_user(message: types.Message, state: FSMContext):
    id_user = message.from_user.id
    await message.answer('Благодарим за отзыв!')
    if len(message.text) < 1024:
        recall = message.text
    else:
        recall = message.text[0:1024]
    await bot.send_message(ADMIN_ID, f"Отзыв:\n{recall}\nОт пользователя: {id_user}")
    await state.finish()


def register_command(dp: Dispatcher):
    dp.register_message_handler(comment, commands=["review"], state="*")
    dp.register_message_handler(help_command, commands=["help"], state="*")
    dp.register_message_handler(comment_user, content_types=["any"], state=CommandAction.st_review)
