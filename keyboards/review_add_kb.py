from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

reviews_cancel = InlineKeyboardButton("Отмена", callback_data="cancel_add_review")

add_reviews_kb = InlineKeyboardMarkup().add(reviews_cancel)