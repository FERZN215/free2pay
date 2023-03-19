from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

delete = InlineKeyboardButton('Удалить', callback_data='seller_delete')
back = InlineKeyboardButton('Назад', callback_data='back_from_one')

seller_kb = InlineKeyboardMarkup().add(delete).add(back)
