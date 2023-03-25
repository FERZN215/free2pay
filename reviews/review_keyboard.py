from aiogram.types import  InlineKeyboardMarkup, InlineKeyboardButton
def reviews_kb(reviews, n):
    reviews_kb = InlineKeyboardMarkup()
    for i in range(len(reviews)):
        if(i>=10):
            break
        cur = InlineKeyboardButton("Автор: "+reviews[i]["name"] +"|Оценка: "+ str(reviews[i]["rating"]), callback_data="review_id:"+str(i))
        reviews_kb.add(cur)
            

    if n == 10 and len(reviews) < 11:
        cancel = InlineKeyboardButton("Cancel", callback_data="cancel_reviews")
        reviews_kb.row(cancel)
    elif n == 10 and len(reviews) == 11:
        forward = InlineKeyboardButton("Вперед", callback_data = "forward_reviews" )
        cancel = InlineKeyboardButton("Cancel", callback_data="cancel_reviews")
        reviews_kb.row(forward)
        reviews_kb.row(cancel)
    elif n > 10 and len(reviews) < 11:
        back= InlineKeyboardButton("Назад", callback_data="back_reviews" )
        cancel = InlineKeyboardButton("Cancel", callback_data="cancel_reviews")
        reviews_kb.row(back)
        reviews_kb.row(cancel)
    else:
        forward = InlineKeyboardButton("Вперед", callback_data = "forward_reviews" )
        back= InlineKeyboardButton("Назад", callback_data="back_reviews" )
        cancel = InlineKeyboardButton("Cancel", callback_data="cancel_reviews")
        reviews_kb.row(back, forward)
        reviews_kb.row(cancel)
    
    return reviews_kb
back = InlineKeyboardButton("Назад", callback_data="back_from_review")
back_kb = InlineKeyboardMarkup().add(back)