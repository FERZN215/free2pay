from aiogram import types
from pymongo.database import Database
from keyboards.personal_area import personal_area_kb

async def personal_area(message:types.Message, db:Database):
    user = db["users"].find_one({"telegram_id":message.chat.id})
    freeze_balnaces = user["freeze_balance"]
    total = 0
    for object in freeze_balnaces:
        total += object["amount"]

    await message.answer("Никнейм: " + user["local_name"] + "\nБаланс: "+ str(user["balance"]) + "\nЗамороженный баланс: " + str(total)+"\nВсего сделок: " + str(user["statistics"]["total"]) + "\nСтатус: " + user["status"], reply_markup=personal_area_kb)
    