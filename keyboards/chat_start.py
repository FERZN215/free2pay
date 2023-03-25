from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton


def chat_start_kb(id):
    yes = InlineKeyboardButton('Начать', callback_data= str(id)+'_chat_start')
    no = InlineKeyboardButton('Отмена', callback_data=str(id)+'_chat_cancel')

    chat_kb = InlineKeyboardMarkup().row(yes, no)
    return chat_kb

def source_kb(id):  
    source_kb = InlineKeyboardMarkup().add(InlineKeyboardButton("Отмена", callback_data=str(id)+"_chat_cancel"))
    return source_kb


stop_kb = ReplyKeyboardMarkup().add(KeyboardButton("Стоп"))
