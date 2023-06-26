from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

post = InlineKeyboardButton('создать предложение', callback_data='sell_post')
redact = InlineKeyboardButton('изменить', callback_data='sell_redact')

sell_conf_kb = InlineKeyboardMarkup().row(post, redact)

