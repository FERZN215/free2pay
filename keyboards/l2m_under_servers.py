from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

serv1 = InlineKeyboardButton('Подсервер 1', callback_data="l2m_under_1")
serv2 = InlineKeyboardButton('Подсервер 2', callback_data="l2m_under_2")
serv3 = InlineKeyboardButton('Подсервер 3', callback_data="l2m_under_3")
serv4 = InlineKeyboardButton('Подсервер 4', callback_data="l2m_under_4")
serv5 = InlineKeyboardButton('Подсервер 5', callback_data="l2m_under_5")
serv6 = InlineKeyboardButton('Подсервер 6', callback_data="l2m_under_6")

l2m_under_servers = InlineKeyboardMarkup().row(serv1, serv2).row(serv3, serv4).row(serv5, serv6)




