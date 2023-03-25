from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

delete = InlineKeyboardButton('Удалить', callback_data='seller_delete')
change_count = InlineKeyboardButton('Изменить количество алмазов', callback_data='seller_count')
back = InlineKeyboardButton('Назад', callback_data='back_from_one')



diamonds_seller_kb = InlineKeyboardMarkup().add(delete).add(change_count).add(back)
