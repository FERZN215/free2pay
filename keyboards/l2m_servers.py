from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

barc = InlineKeyboardButton('Барц', callback_data='l2m_server_barc')
zighard = InlineKeyboardButton('Зигхард', callback_data='l2m_server_zighard')
leona = InlineKeyboardButton('Леона', callback_data='l2m_server_leona')
erika = InlineKeyboardButton('Эрика', callback_data='l2m_server_erika')


l2m_servers = InlineKeyboardMarkup().row(barc, zighard).row(leona, erika)




