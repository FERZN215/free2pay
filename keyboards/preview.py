from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

registration = InlineKeyboardButton("Регистрация", callback_data="registration")
rules = InlineKeyboardButton("Правила", url='https://docs.google.com/document/d/1z4DwPFGdHvhsVY0ym7ECTy7cuwxb-Z2W')
faq = InlineKeyboardButton("FAQ", url='https://docs.google.com/document/d/1z4DwPFGdHvhsVY0ym7ECTy7cuwxb-Z2W')
about_us = InlineKeyboardButton("О нас", url='https://docs.google.com/document/d/1z4DwPFGdHvhsVY0ym7ECTy7cuwxb-Z2W')

preview_kb = InlineKeyboardMarkup().add(registration).row(rules, faq).add(about_us)
  