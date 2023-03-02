from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

license_agreement = InlineKeyboardButton("Лицензионное соглашение", url='https://docs.google.com/document/d/1z4DwPFGdHvhsVY0ym7ECTy7cuwxb-Z2W')
yes = InlineKeyboardButton("Принимаю", callback_data="license_yes")
no = InlineKeyboardButton("Отклоняю", callback_data="license_no")
license_agreement_kb = InlineKeyboardMarkup().add(license_agreement).row(yes, no)