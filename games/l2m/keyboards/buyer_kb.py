from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

buy = InlineKeyboardButton('Купить', callback_data='buyer_buy')
chat = InlineKeyboardButton('Чат', callback_data='buyer_chat')
reviews = InlineKeyboardButton('Отзывы', callback_data='buyer_reviews')
report = InlineKeyboardButton('Пожаловаться', callback_data='buyer_report')
back = InlineKeyboardButton('Назад', callback_data='back_from_one')



buyer_kb = InlineKeyboardMarkup().add(buy).add(chat, reviews).add(report, back)
