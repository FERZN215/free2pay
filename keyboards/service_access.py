from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

def service_access(id):
    correct = InlineKeyboardButton('Успешно', callback_data='buyer_accept:'+str(id))
    chat = InlineKeyboardButton('Чат', callback_data='buyer_chat:'+str(id))

    report = InlineKeyboardButton('Пожаловаться', callback_data='buyer_report'+str(id))


    access_kb = InlineKeyboardMarkup().add(correct).add(chat, report)
    return access_kb