from aiogram.types import ReplyKeyboardMarkup, KeyboardButton


active_deals = KeyboardButton("Активные сделки")
profile = KeyboardButton("Профиль")
buy = KeyboardButton("Купить")
sell = KeyboardButton("Продать")
top_up = KeyboardButton("Пополнить")
withdraw = KeyboardButton("Вывести")
help = KeyboardButton("Поддержка")
chat = KeyboardButton('Мои чаты')

menu_kb = ReplyKeyboardMarkup(resize_keyboard=True).add(active_deals, chat).row(buy, sell).row(top_up, withdraw).add(profile, help)