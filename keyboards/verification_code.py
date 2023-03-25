from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

def access_code(id):
    correct = InlineKeyboardButton('Успешно', callback_data='buyer_accept:'+str(id))

    code_query = InlineKeyboardButton('Запросить код', callback_data='buyer_code_query:'+str(id))
    chat = InlineKeyboardButton('Чат', callback_data='buyer_chat:'+str(id))

    report = InlineKeyboardButton('Пожаловаться', callback_data='buyer_report'+str(id))


    access_kb = InlineKeyboardMarkup().add(correct).add(code_query).add(chat, report)
    return access_kb