from aiogram.types import  InlineKeyboardMarkup, InlineKeyboardButton
from usefull.converters import game_converter

def my_chats_kb(deals, n, send, db):
    deals_kb = InlineKeyboardMarkup()
    for i in range(len(deals)):
        if i>=10 or i >=len(deals):
            break
        
        chat = db["chats"].find_one({"_id":deals[i]})

        offer = db[chat["game"]].find_one({"_id":chat["offer"]})


        if send == offer["seller"]:
            if chat["target"] == send:
                buyer = db["users"].find_one({"telegram_id":chat["source"]})
                text = "Покупатель" + str(buyer["local_name"]) + "|"
            else:
                buyer = db["users"].find_one({"telegram_id":chat["target"]})
                text = "Покупатель" + str(buyer["local_name"]) + "|"
        else:
            if chat["target"] == send:
                seller = db["users"].find_one({"telegram_id":chat["source"]})
                text = "Продавец:"+ str(seller["local_name"]) + "|"
            else:
                seller = db["users"].find_one({"telegram_id":chat["target"]})
                text = "Продавец:"+ str(seller["local_name"]) + "|"



        cur = InlineKeyboardButton(text + game_converter(offer["game"], offer["pr_type"]) + "|Цена: "+str(offer["cost"]), callback_data="my_chmat_id:"+str(chat["_id"]))
        deals_kb.add(cur)



    if n == 10 and len(deals) < 11:
        cancel = InlineKeyboardButton("Cancel", callback_data="cancel_chats")
        deals_kb.row(cancel)
    elif n == 10 and len(deals) == 11:
        forward = InlineKeyboardButton("Вперед", callback_data = "forward_chats" )
        cancel = InlineKeyboardButton("Cancel", callback_data="cancel_chats")
        deals_kb.row(forward)
        deals_kb.row(cancel)
    elif n > 10 and len(deals) < 11:
        back= InlineKeyboardButton("Назад", callback_data="back_chats" )
        cancel = InlineKeyboardButton("Cancel", callback_data="cancel_chats")
        deals_kb.row(back)
        deals_kb.row(cancel)
    else:
        forward = InlineKeyboardButton("Вперед", callback_data = "forward_chats" )
        back= InlineKeyboardButton("Назад", callback_data="back_chats" )
        cancel = InlineKeyboardButton("Cancel", callback_data="cancel_chats")
        deals_kb.row(back, forward)
        deals_kb.row(cancel)
    


    return deals_kb


def one_chat_kb(id, game):

    one_chat_kb = InlineKeyboardMarkup().add(
        InlineKeyboardButton("Начать чат", callback_data=str(game)+'_m_buyer_cha_'+str(id) ),
        InlineKeyboardButton("Назад", callback_data="back_to_one_chat")

        )
    return one_chat_kb