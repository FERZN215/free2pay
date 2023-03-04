from aiogram import types

async def reviews_process(message: types.Message, db):
    user = db["users"].find_one({"telegram_id":message.chat.id})
    reviews = user["reviews"]
    for review in reviews:
        print(review)
