from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

orb = InlineKeyboardButton('Орб', callback_data='account_orb')
posox = InlineKeyboardButton('Посох', callback_data='account_posox')
kinj = InlineKeyboardButton('Кинжал', callback_data='account_kinj')
luk = InlineKeyboardButton('Лук', callback_data='account_luk')
arbal = InlineKeyboardButton('Арбалет', callback_data='account_arbal')
dual = InlineKeyboardButton('Дуалы', callback_data='account_dual')
shit = InlineKeyboardButton('Щит', callback_data='account_shield')#shit ))))
glefa = InlineKeyboardButton('Глефа', callback_data='account_glefa')
d_mech = InlineKeyboardButton('Двуручный меч', callback_data='account_double_sword')

l2m_account_cat = InlineKeyboardMarkup().row(orb, posox, kinj).row(luk, arbal, dual).row(shit, glefa, d_mech)
