from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

reviews = KeyboardButton("Отзывы")
deals = KeyboardButton("Сделки")


personal_area_kb = ReplyKeyboardMarkup(resize_keyboard=True).row(reviews, deals)     