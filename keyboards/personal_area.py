from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

reviews = InlineKeyboardButton("Отзывы", callback_data="all_reviews")
deals = InlineKeyboardButton("МОИ ТОВАРЫ", callback_data="all_offers")
back = InlineKeyboardButton("Назад", callback_data="all_back")


personal_area_kb = InlineKeyboardMarkup().row(reviews, deals).add(back)    