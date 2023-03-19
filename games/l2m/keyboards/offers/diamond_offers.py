from aiogram.types import  InlineKeyboardMarkup, InlineKeyboardButton
from usefull.com_sw import com_sw
def offers_kb(posts, n, db, sort="cost"):
    offers_kb = InlineKeyboardMarkup()
    for i in range(len(posts)):
        if(i>=10):
            break
        seller = db["users"].find_one({"telegram_id":posts[i]["seller"]})
        if seller["statistics"]["total"] >0:
            rat = seller["statistics"]["successful"] / (seller["statistics"]["total"]/100)
        else:
            rat = 0
        cur = InlineKeyboardButton("Продавец: "+seller["local_name"] +"|Кол-во: "+str(posts[i]["name"])+"|Цена(eд.): "+str(posts[i]["cost"])+"|Комиссия: "+str(com_sw(posts[i]["comission"])) + "|Рейтинг: "+str(rat)+"%", callback_data="dia_offer_id:"+str(posts[i]["_id"]))
        offers_kb.add(cur)

    match sort:
        case "cost":
            offers_kb.add(InlineKeyboardButton("По количеству", callback_data="count_offers"))
        case "name":
            offers_kb.add(InlineKeyboardButton("По цене", callback_data="cost_offers"))

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