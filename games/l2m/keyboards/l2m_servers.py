from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

barc = InlineKeyboardButton('Барц', callback_data='server_l2m_barc')
zighard = InlineKeyboardButton('Зигхард', callback_data='server_l2m_zighard')
leona = InlineKeyboardButton('Леона', callback_data='server_l2m_leona')
erika = InlineKeyboardButton('Эрика', callback_data='server_l2m_erika')


l2m_servers = InlineKeyboardMarkup().row(barc, zighard).row(leona, erika)




