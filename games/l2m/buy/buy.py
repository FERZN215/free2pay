from aiogram.dispatcher import FSMContext
from aiogram import types
from pymongo.database import Database
from aiogram.dispatcher.filters.state import State, StatesGroup
from bson.objectid import ObjectId

from ..keyboards.no_balance import no_balance_kb

from balance.b_add import balance_add_summ
from start.preview import preview
class buy_list(StatesGroup):
    buy_start = State()


async def diamond_buy_process(call:types.CallbackQuery, state:FSMContext, db:Database):
    await buy_list.buy_start.set()
    data = await state.get_data()
    buyer = db["users"].find_one({"telegram_id":call.message.chat.id})
    if buyer["balance"] < data.get("sum"):
        await call.message.answer("На вашем счету недостаточно средств", reply_markup=no_balance_kb)
        return
    db["users"].update_one({"telegram_id":call.message.chat.id}, {"$inc":{"balance":-float(data.get("sum"))}})
    db["l2m"].update_one({"_id":data.get("id")}, {"$inc":{"name":-int(data.get("buy_count"))}})




async def buy_process(call:types.CallbackQuery, state:FSMContext, db:Database):
    await buy_list.buy_start.set()
    data = await state.get_data()
    buyer = db["users"].find_one({"telegram_id":call.message.chat.id})
    offer = db["l2m"].find_one({"_id":data.get("id")})
    if buyer["balance"] < offer["cost"]:
        await call.message.answer("На вашем счету недостаточно средств", reply_markup=no_balance_kb)
        return
    db["users"].update_one({"telegram_id":call.message.chat.id}, {"$inc":{"balance":-float(offer["cost"])}})

  





#-------------------balance--------------------------
async def balance_add_process(call:types.CallbackQuery, state:FSMContext, db:Database):
    await balance_add_summ(call.message, state)
   

async def buy_cancel(call:types.CallbackQuery, state:FSMContext, db:Database):
    await state.finish()
    await preview(call.message, db)