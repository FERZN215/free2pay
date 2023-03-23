from aiogram.dispatcher import FSMContext
from aiogram import types
from pymongo.database import Database
from aiogram.dispatcher.filters.state import State, StatesGroup
from keyboards.deals_kb import active_deals_kb


async def deals_process(message:types.Message, db:Database):
    user = db["users"].find_one({"telegram_id":message.chat.id})
    deals = []
    for deal in user["deals"][:11]:
        deals.append(deal)