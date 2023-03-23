from aiogram import types
from pymongo.database import Database
async def reviews_process(message: types.Message, db:Database):
    user = db["users"].find_one({"telegram_id":message.chat.id})
    reviews = user["reviews"]
    for review in reviews:
        print(review)
