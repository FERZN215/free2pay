from aiogram.dispatcher import FSMContext
from aiogram import types
from pymongo.database import Database
from aiogram.dispatcher.filters.state import State, StatesGroup
from bson.objectid import ObjectId

from aiogram import Bot, Dispatcher

from reviews.reviews_add import reviews_add

from keyboards.buy_start import buy_start_kb
from ..keyboards.thing_sell_type import thing_sell_type_kb, au_buyer_kb

from keyboards.menu import menu_kb
from ..keyboards.no_balance import no_balance_kb
from keyboards.verification_code import access_code
from keyboards.service_access import service_access
from usefull.converters import *

from balance.b_add import balance_add_summ
from start.preview import preview

from usefull.is_digit import is_digit
class buy_list(StatesGroup):
    buy_start = State()
    seller_ready = State()
    login_input =   State()
    password_input = State()
    verification_code = State()
    thing_sell_type = State()
    au_cost = State()
    trade_desc = State()
    service_instruction = State()


#------------------------------------------------------------------------------------------------------------------------------------------------------

async def buy_process_start_com(call:types.CallbackQuery, state:FSMContext, db:Database):
    data = await state.get_data()
    buyer = db["users"].find_one({"telegram_id":call.message.chat.id})
    offer = db["l2m"].find_one({"_id":data.get("id")})
   
    if buyer["balance"] < offer["cost"]:
        await call.message.answer("На вашем счету недостаточно средств", reply_markup=no_balance_kb)
        return
    db["l2m"].update_one({"_id":data.get("id")}, {"$set":{"invis":True}})
    db["users"].update_one({"telegram_id":call.message.chat.id}, {"$inc":{"balance":-float(offer["cost"])}})
    active_deal = {"status":"seller await", "game":data.get("game"), "category":data.get("game_type"), "seller":offer["seller"], "buyer":call.message.chat.id, "offer_id":data.get("id"), "cost": offer["cost"]}
    db["active_deals"].insert_one(active_deal)
    db["users"].update_one({"telegram_id":call.message.chat.id}, {"$push":{"deals":active_deal["_id"]}})
    db["users"].update_one({"telegram_id":offer["seller"]}, {"$push":{"deals":active_deal["_id"]}})
    
    await call.message.answer("Продавцу отправлено уведомление, ожидайте", reply_markup=menu_kb)
    return {
        "offer":offer,
        "active_deal":active_deal
            }


async def buyer_accept(call:types.CallbackQuery, state:FSMContext, db:Database, bot:Bot):
    try:
        offer = db["active_deals"].find_one({"_id":ObjectId(call.data.replace("buyer_accept:", ""))})
    except:
        await call.message.answer("Сделка уже завершена")
        return

    if offer["status"] != "buyer awaiting":
       
        await call.message.answer("Самсинг вент вронг(")
        return
    
    db["users"].update_one({"telegram_id":offer["seller"]}, {"$inc":{"balance":offer["cost"]}})
    db["active_deals"].update_one({"_id":ObjectId(offer["_id"])}, {"$set":{"status":"well done"}})
    db["l2m"].delete_one({"_id":offer["offer_id"]})

    db["users"].update_one({"telegram_id":offer["seller"]}, {"$inc":{"statistics.successful":1}})

    await bot.send_message(offer["seller"], "Покупатель подтвердил выполнение заказа, на ваш баланс зачисленно "+ str(offer["cost"]))
    await call.message.answer("Поздравляем с приобретением!")
    await state.update_data(seller_id_r = offer["seller"])
    await reviews_add(call, state)

    #await state.finish()

async def buy_process(call:types.CallbackQuery, state:FSMContext, db:Database):
    # await buy_list.buy_start.set()
    # data = await state.get_data()a
    # buyer = db["users"].find_one({"telegram_id":call.message.chat.id})
    # offer = db["l2m"].find_one({"_id":data.get("id")})
    # if buyer["balance"] < offer["cost"]:
    #     await call.message.answer("На вашем счету недостаточно средств", reply_markup=no_balance_kb)
    #     return
    # db["users"].update_one({"telegram_id":call.message.chat.id}, {"$inc":{"balance":-float(offer["cost"])}})

    pass




#-------------------balance--------------------------
async def balance_add_process(call:types.CallbackQuery, state:FSMContext, db:Database):
    await balance_add_summ(call.message, state)
   

async def buy_cancel(call:types.CallbackQuery, state:FSMContext, db:Database):
    await state.finish()
    await preview(call.message, db)



