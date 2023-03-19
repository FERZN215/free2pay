from aiogram.types import  InlineKeyboardMarkup, InlineKeyboardButton
def offers_kb(posts, n, db):
    offers_kb = InlineKeyboardMarkup()
    for i in range(len(posts)):
        if(i>=10):
            break
        seller_name = db["users"].find_one({"telegram_id":posts[i]["seller"]})["local_name"]
        cur = InlineKeyboardButton("Продавец: "+seller_name +"|Описание:"+ posts[i]["description"][:45] +"|Цена: "+str(posts[i]["cost"]) + "|100%", callback_data="ser_offer_id:"+str(posts[i]["_id"]))
        offers_kb.add(cur)



    if n == 10 and len(posts) < 11:
        cancel = InlineKeyboardButton("Cancel", callback_data="cancel_offers")
        offers_kb.row(cancel)
    elif n == 10 and len(posts) == 11:
        forward = InlineKeyboardButton("Вперед", callback_data = "forward_offers" )
        cancel = InlineKeyboardButton("Cancel", callback_data="cancel_offers")
        offers_kb.row(forward)
        offers_kb.row(cancel)
    elif n > 10 and len(posts) < 11:
        back= InlineKeyboardButton("Назад", callback_data="back_offers" )
        cancel = InlineKeyboardButton("Cancel", callback_data="cancel_offers")
        offers_kb.row(back)
        offers_kb.row(cancel)
    else:
        forward = InlineKeyboardButton("Вперед", callback_data = "forward_offers" )
        back= InlineKeyboardButton("Назад", callback_data="back_offers" )
        cancel = InlineKeyboardButton("Cancel", callback_data="cancel_offers")
        offers_kb.row(back, forward)
        offers_kb.row(cancel)
    


    return offers_kb