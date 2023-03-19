from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

serv1 = InlineKeyboardButton('Подсервер 1', callback_data="under_s_l2m_1")
serv2 = InlineKeyboardButton('Подсервер 2', callback_data="under_s_l2m_2")
serv3 = InlineKeyboardButton('Подсервер 3', callback_data="under_s_l2m_3")
serv4 = InlineKeyboardButton('Подсервер 4', callback_data="under_s_l2m_4")
serv5 = InlineKeyboardButton('Подсервер 5', callback_data="under_s_l2m_5")
serv6 = InlineKeyboardButton('Подсервер 6', callback_data="under_s_l2m_6")

l2m_under_servers = InlineKeyboardMarkup().row(serv1, serv2).row(serv3, serv4).row(serv5, serv6)




