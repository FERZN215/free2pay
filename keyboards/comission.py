from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

yes = InlineKeyboardButton('Да', callback_data='comission_yes')
no = InlineKeyboardButton('Нет', callback_data='comission_no')

comission_kb = InlineKeyboardMarkup().row(yes, no)