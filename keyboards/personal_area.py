from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
reviews = InlineKeyboardButton("Отзывы", callback_data="reviwes")
full_statistic = InlineKeyboardButton("Статистика", callback_data="full_statistic")
deals = InlineKeyboardButton("Сделки", callback_data="deals")

buy = InlineKeyboardButton("Купить", callback_data="buy")
sell = InlineKeyboardButton("Продать", callback_data="sell")

top_up = InlineKeyboardButton("Пополнить", callback_data="top_up")
withdraw = InlineKeyboardButton("Вывести", callback_data="withdraw")

help = InlineKeyboardButton("Поддержка", callback_data="help")
personal_area_kb = InlineKeyboardMarkup().row(buy, sell).row(top_up, withdraw).row(reviews, full_statistic, deals).add(help)