from aiogram.types import  InlineKeyboardMarkup, InlineKeyboardButton
def offers_kb( posts, n):
    offers_kb = InlineKeyboardMarkup()
    for i in range(n-10, len(posts)):
        if i >= n or i > len(posts):
            break
        else:
            cur = InlineKeyboardButton(str(posts[i]["count"]), callback_data="offer_id:"+str(posts[i]["_id"]))
            offers_kb.add(cur)
    if n <= 10 and n >= len(posts):
        cancel = InlineKeyboardButton("Cancel", callback_data="cancel_offers")
        offers_kb.row(cancel)
    elif n == 10:
        forward = InlineKeyboardButton("Вперед", callback_data = "forward_offers", switch_pm_text='Loading more...', switch_pm_parameter='list_products' )
        cancel = InlineKeyboardButton("Cancel", callback_data="cancel_offers")
        offers_kb.row(forward)
        offers_kb.row(cancel)
    elif n>=len(posts):
        back= InlineKeyboardButton("Назад", callback_data="back_offers", switch_pm_text='Loading more...', switch_pm_parameter='list_products' )
        cancel = InlineKeyboardButton("Cancel", callback_data="cancel_offers")
        offers_kb.row(back)
        offers_kb.row(cancel)
    else:
        forward = InlineKeyboardButton("Вперед", callback_data = "forward_offers", switch_pm_text='Loading more...', switch_pm_parameter='list_products' )
        back= InlineKeyboardButton("Назад", callback_data="back_offers", switch_pm_text='Loading more...', switch_pm_parameter='list_products' )
        cancel = InlineKeyboardButton("Cancel", callback_data="cancel_offers")
        offers_kb.row(back, forward)
        offers_kb.row(cancel)
    return offers_kb