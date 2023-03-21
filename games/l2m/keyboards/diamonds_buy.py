from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

buy = InlineKeyboardButton('Оплатить', callback_data='button_buy')
change_count = InlineKeyboardButton('Изменить количество алмазов', callback_data='button_change_dia')
cancel = InlineKeyboardButton('Отменить', callback_data='button_cancel_buy')


diamond_buy_kb = InlineKeyboardMarkup().add(buy).add(change_count).add(cancel)
