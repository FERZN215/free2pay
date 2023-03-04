from aiogram import types

async def deals_process(message:types.Message, db):
    user = db["users"].find_one({"telegram_id":message.chat.id})
    deals = user["deals"]
    for deal in deals:
        print(deal)