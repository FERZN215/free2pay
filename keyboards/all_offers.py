from aiogram.types import  InlineKeyboardMarkup, InlineKeyboardButton
from usefull.converters import game_converter
def all_offers_kb(offers, n):
    offers_kb = InlineKeyboardMarkup()
    for i in range(len(offers)):
        if i>=10 or i >=len(offers):
            break
        
       


        cur = InlineKeyboardButton(game_converter(offers[i]["game"], offers[i]["pr_type"]) + "|Цена: "+str(offers[i]["cost"]), callback_data="all_offer_id:"+str(offers[i]["_id"]))
        offers_kb.add(cur)



    if n == 10 and len(offers) < 11:
        cancel = InlineKeyboardButton("Cancel", callback_data="cancel_alloffers")
        offers_kb.row(cancel)
    elif n == 10 and len(offers) == 11:
        forward = InlineKeyboardButton("Вперед", callback_data = "forward_alloffers" )
        cancel = InlineKeyboardButton("Cancel", callback_data="cancel_alloffers")
        offers_kb.row(forward)
        offers_kb.row(cancel)
    elif n > 10 and len(offers) < 11:
        back= InlineKeyboardButton("Назад", callback_data="back_alloffers" )
        cancel = InlineKeyboardButton("Cancel", callback_data="cancel_alloffers")
        offers_kb.row(back)
        offers_kb.row(cancel)
    else:
        forward = InlineKeyboardButton("Вперед", callback_data = "forward_alloffers" )
        back= InlineKeyboardButton("Назад", callback_data="back_alloffers" )
        cancel = InlineKeyboardButton("Cancel", callback_data="cancel_alloffers")
        offers_kb.row(back, forward)
        offers_kb.row(cancel)

    return offers_kb