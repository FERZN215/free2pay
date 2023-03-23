from aiogram.types import  InlineKeyboardMarkup, InlineKeyboardButton

def active_deals_kb(deals, n,send, db):
    deals_kb = InlineKeyboardMarkup()
    for i in range(len(deals)):
        if(i>=10):
            break
        
        if deals[i]["buyer"] == send:
            seller = db["users"].find_one({"telegram_id":deals[i]["seller"]})
            text = "Продавец:"+ str(seller["local_name"]) + "|"
        else:
            buyer = db["users"].find_one({"telegram_id":deals[i]["buyer"]})
            text = "Покупатель" + str(buyer["local_name"]) + "|"

        cur = InlineKeyboardButton(text + converter(deals[i]["game"], deals[i]["category"]) + "|Цена: "+str(deals[i]["cost"])+"|Статус: " + status(deals[i]["status"]), callback_data="active_deal_id:"+str(deals[i]["_id"]))
        deals_kb.add(cur)



    if n == 10 and len(deals) < 11:
        cancel = InlineKeyboardButton("Cancel", callback_data="cancel_offers")
        deals_kb.row(cancel)
    elif n == 10 and len(deals) == 11:
        forward = InlineKeyboardButton("Вперед", callback_data = "forward_offers" )
        cancel = InlineKeyboardButton("Cancel", callback_data="cancel_offers")
        deals_kb.row(forward)
        deals_kb.row(cancel)
    elif n > 10 and len(deals) < 11:
        back= InlineKeyboardButton("Назад", callback_data="back_offers" )
        cancel = InlineKeyboardButton("Cancel", callback_data="cancel_offers")
        deals_kb.row(back)
        deals_kb.row(cancel)
    else:
        forward = InlineKeyboardButton("Вперед", callback_data = "forward_offers" )
        back= InlineKeyboardButton("Назад", callback_data="back_offers" )
        cancel = InlineKeyboardButton("Cancel", callback_data="cancel_offers")
        deals_kb.row(back, forward)
        deals_kb.row(cancel)
    


    return deals_kb

def converter(game:str, type:str):
    match game:
        case "game_lage2m":
            match type:
                case "cat_accounts":
                    return "Игра: Lineage 2M|Тип товара: Аккаунты"
                case "cat_diamonds":
                    return "Игра: Lineage 2M|Тип товара: Алмазы"
                case "cat_things":
                    return "Игра: Lineage 2M|Тип товара: Предметы"
                case "cat_services":
                    return "Игра: Lineage 2M|Тип товара: Услуги"
                
def status(st:str):
    match st:
        case "seller await":
            return "Ожидаем продавца"
        case "seller accepted":
            return "Продавец принял"
        case "buyer awaiting":
            return "Ожидаем покупателя"
        case "well done":
            return "Завершена"