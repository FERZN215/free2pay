from aiogram import types
from pymongo.database import Database
async def deals_process(message:types.Message, db:Database):
    user = db["users"].find_one({"telegram_id":message.chat.id})
    deals = user["deals"]
    for deal in deals:
        print(deal)