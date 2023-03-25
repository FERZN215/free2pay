from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton



au = InlineKeyboardButton('Аукцион', callback_data='thing_sell_au')
trade = InlineKeyboardButton('Трейд', callback_data='thing_sell_trade')

thing_sell_type_kb = InlineKeyboardMarkup().add(au, trade)


def au_buyer_kb(id):
    accept = InlineKeyboardButton('Согласиться', callback_data=str(id)+'_buyer_au_accept')
    disagree = InlineKeyboardButton('Отказаться', callback_data=str(id)+'_buyer_au_dis')
    au_buyer_kb = InlineKeyboardMarkup().add(accept, disagree)
    return au_buyer_kb