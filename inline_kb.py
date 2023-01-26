from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

inline_game_km = InlineKeyboardMarkup(row_width=1,
                                      inline_keyboard=[
                                          [
                                              InlineKeyboardButton(
                                                  text='✅ Да',
                                                  callback_data='yep'
                                              ),
                                              InlineKeyboardButton(
                                                  text='❎ Нет',
                                                  callback_data='nope'
                                              )
                                          ]
                                      ])

inline_choose = InlineKeyboardMarkup(row_width=1,
                                     inline_keyboard=[
                                         [
                                             InlineKeyboardButton(
                                                 text='⬆ Взять карту',
                                                 callback_data='plus'
                                             ),
                                             InlineKeyboardButton(
                                                 text='⬇ Оставить карты',
                                                 callback_data='minus'
                                             )],
                                         [
                                             InlineKeyboardButton(
                                                 text='💬 В меню',
                                                 callback_data='start'
                                             )
                                         ]
                                     ])

inline_menu = InlineKeyboardMarkup(row_width=1,
                                   inline_keyboard=[
                                       [
                                           InlineKeyboardButton(
                                               text='🃏 Новая игра',
                                               callback_data='plus'
                                           ),
                                           InlineKeyboardButton(
                                               text='📶 Online',
                                               callback_data='online_game'
                                           )],
                                       [
                                           InlineKeyboardButton(
                                               text='🏆 Статистика',
                                               callback_data='result'
                                           )],
                                       [
                                           InlineKeyboardButton(
                                               text='💬 В меню',
                                               callback_data='start'
                                           )
                                       ]
                                   ])

inline_choose2 = InlineKeyboardMarkup(row_width=1,
                                      inline_keyboard=[
                                          [
                                              InlineKeyboardButton(
                                                  text='Взять карту',
                                                  callback_data='plus_multy'
                                              ),
                                              InlineKeyboardButton(
                                                  text='Оставить карты',
                                                  callback_data='minus_multy'
                                              )],
                                          [
                                              InlineKeyboardButton(
                                                  text='Сдаться',
                                                  callback_data='loser'
                                              )
                                          ]
                                      ])
