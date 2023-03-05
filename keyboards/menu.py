from aiogram.types import ReplyKeyboardMarkup, KeyboardButton


active_deals = KeyboardButton("Активные сделки")
profile = KeyboardButton("Профиль")
buy = KeyboardButton("Купить")
sell = KeyboardButton("Продать")
top_up = KeyboardButton("Пополнить")
withdraw = KeyboardButton("Вывести")
help = KeyboardButton("Поддержка")

menu_kb = ReplyKeyboardMarkup(resize_keyboard=True).add(active_deals).row(buy, sell).row(top_up, withdraw).add(profile, help)