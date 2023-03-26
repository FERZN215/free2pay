from aiogram import types
from pymongo.database import Database
from keyboards.personal_area import personal_area_kb
from usefull.converters import status_to_text
from aiogram.dispatcher.filters.state import State, StatesGroup

class Profile(StatesGroup):
    profile = State()

async def personal_area(message:types.Message, db:Database):
    await Profile.profile.set()
    user = db["users"].find_one({"telegram_id":message.chat.id})
    freeze_balnaces = user["freeze_balance"]
    total = 0
    for object in freeze_balnaces:
        total += object["amount"]
    if user["statistics"]["total"] >0:
            rat = user["statistics"]["successful"] / (user["statistics"]["total"]/100)
    else:
        rat = 0
    await message.answer(
        "Никнейм: " + user["local_name"] +
        "\nБаланс: "+ str(user["balance"]) + 
        "\nЗамороженный баланс: " + str(total)+
        "\nВсего сделок: " + str(user["statistics"]["total"]) + 
        "\nУспешных: " + str(user["statistics"]["successful"]) +
        "\nНеудачных: " + str(user["statistics"]["arbitration"]) + 

        "\nСтатус: " + status_to_text(user["status"])+ 

        "\nПредупреждения: "+ str(user["warns"])+
        "\nРейтинг: " + str(rat) + "%", 
        reply_markup=personal_area_kb)
    