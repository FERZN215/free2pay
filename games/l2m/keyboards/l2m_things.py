from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

weapon = InlineKeyboardButton('Оружие', callback_data='things_weapon')
armor = InlineKeyboardButton('Броня', callback_data='things_armor')
acces = InlineKeyboardButton('Аксессуары', callback_data='things_accessories')
oth = InlineKeyboardButton('Прочее', callback_data='things_other')


l2m_things_cat = InlineKeyboardMarkup().add(weapon).add(armor).add(acces).add(oth)
