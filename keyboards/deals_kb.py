from aiogram.types import  InlineKeyboardMarkup, InlineKeyboardButton

def active_deals_kb(deals, n,send, db):
    deals_kb = InlineKeyboardMarkup()
    for i in range(len(deals)):
        if i>=10 or i >=len(deals):
            break
        
        deal = db["active_deals"].find_one({"_id":deals[i]})
        if(deal["status"] == "well done"):
            continue

        if deal["buyer"] == send:
            seller = db["users"].find_one({"telegram_id":deal["seller"]})
            text = "Продавец:"+ str(seller["local_name"]) + "|"
        else:
            buyer = db["users"].find_one({"telegram_id":deal["buyer"]})
            text = "Покупатель" + str(buyer["local_name"]) + "|"

        cur = InlineKeyboardButton(text + converter(deal["game"], deal["category"]) + "|Цена: "+str(deal["cost"])+"|Статус: " + status(deal["status"]), callback_data="active_deal_id:"+str(deal["_id"]))
        deals_kb.add(cur)



    if n == 10 and len(deals) < 11:
        cancel = InlineKeyboardButton("Cancel", callback_data="cancel_deals")
        deals_kb.row(cancel)
    elif n == 10 and len(deals) == 11:
        forward = InlineKeyboardButton("Вперед", callback_data = "forward_deals" )
        cancel = InlineKeyboardButton("Cancel", callback_data="cancel_deals")
        deals_kb.row(forward)
        deals_kb.row(cancel)
    elif n > 10 and len(deals) < 11:
        back= InlineKeyboardButton("Назад", callback_data="back_deals" )
        cancel = InlineKeyboardButton("Cancel", callback_data="cancel_deals")
        deals_kb.row(back)
        deals_kb.row(cancel)
    else:
        forward = InlineKeyboardButton("Вперед", callback_data = "forward_deals" )
        back= InlineKeyboardButton("Назад", callback_data="back_deals" )
        cancel = InlineKeyboardButton("Cancel", callback_data="cancel_deals")
        deals_kb.row(back, forward)
        deals_kb.row(cancel)
    


    return deals_kb




def one_active_deal_kb_seller(status:str, id:str):
    deal_kb = InlineKeyboardMarkup()
    match status:
        case "seller await":
            accept = InlineKeyboardButton("Начать сделку", callback_data=str(id)+"_one_yes")
            cancel = InlineKeyboardButton("Отменить покупку", callback_data=str(id)+"_one_no")
            deal_kb.add(accept, cancel)
        case "seller accepted":
            accept = InlineKeyboardButton("Подтвердить выполнение", callback_data=str(id)+"_one_seller_accept")
            report = InlineKeyboardButton("Арбитраж", callback_data=str(id)+"_one_report")
            deal_kb.add(report)
        case "buyer awaiting":
            # accept_get = InlineKeyboardButton("Подтвердить получение", callback_data=str(id)+"_one_accept  ")
            report = InlineKeyboardButton("Арбитраж", callback_data=str(id)+"_one_report")
            deal_kb.add(report)
        # case "well done":
        #     return "Завершена"
        case "report":
            decision = InlineKeyboardButton("Посмотреть ответ арбитража", callback_data=str(id)+"_one_decision")
            deal_kb.add(decision)
    
    deal_kb.add(InlineKeyboardButton("Назад", callback_data="back_from_deals"))
    return deal_kb
        
def one_active_deal_kb_buyer(status:str, id:str):
    deal_kb = InlineKeyboardMarkup()
    match status:
        case "seller await":
            cancel = InlineKeyboardButton("Отменить покупку", callback_data=str(id)+"_one_buyer_no")
            deal_kb.add(cancel)
        case "seller accepted":
            report = InlineKeyboardButton("Арбитраж", callback_data=str(id)+"_one_report")
            deal_kb.add(report)
        case "buyer awaiting":
            accept_get = InlineKeyboardButton("Подтвердить получение", callback_data=str(id)+"_one_buyer_accept")
            report = InlineKeyboardButton("Арбитраж", callback_data=str(id)+"_one_report")
            deal_kb.add(accept_get, report)
        # case "well done":
        #     return "Завершена"
        case "report":
            decision = InlineKeyboardButton("Посмотреть ответ арбитража", callback_data=str(id)+"_one_decision")
            deal_kb.add(decision)
    
    deal_kb.add(InlineKeyboardButton("Назад", callback_data="back_from_deals"))
    return deal_kb







def converter(game:str, type:str)->str:
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
                
def status(st:str)->str:
    match st:
        case "seller await":
            return "Ожидаем продавца"
        case "seller accepted":
            return "Продавец принял"
        case "buyer awaiting":
            return "Ожидаем покупателя"
        case "well done":
            return "Завершена"
        case "report":
            return "Арбитраж"