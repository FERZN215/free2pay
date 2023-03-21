from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

b_add = InlineKeyboardButton('Пополнить', callback_data='no_balance_add')
cancel = InlineKeyboardButton('Отменить', callback_data='no_balance_cancel')




no_balance_kb = InlineKeyboardMarkup().add(b_add).add(cancel)
