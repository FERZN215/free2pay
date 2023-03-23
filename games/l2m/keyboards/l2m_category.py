from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

accounts = InlineKeyboardButton('Аккаунты', callback_data='cat_accounts')
diamonds = InlineKeyboardButton('Алмазы', callback_data='cat_diamonds')
things = InlineKeyboardButton('Предметы', callback_data='cat_things')
services = InlineKeyboardButton('Услуги', callback_data='cat_services')


l2m_category_kb = InlineKeyboardMarkup().add(accounts).add(diamonds).add(services).add(things)
