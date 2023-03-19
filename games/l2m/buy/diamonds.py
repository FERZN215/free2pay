from aiogram.dispatcher import FSMContext
from aiogram import types
from pymongo.database import Database
from aiogram.dispatcher.filters.state import State, StatesGroup
from bson.objectid import ObjectId
from ..keyboards.offers.diamond_offers import offers_kb
from usefull.com_sw import com_sw
from ..keyboards.diamond_seller_kb import diamonds_seller_kb
from ..keyboards.buyer_kb import buyer_kb

class diamonds_list(StatesGroup):
    cur_list = State()
    sort = State()
    id = State()

async def diamonds_out(call:types.CallbackQuery, state:FSMContext, db:Database):
    data = await state.get_data()
    offers = []
    for offer in db["l2m"].find({"game":data.get("game"),"pr_type":data.get("game_type"), "server":data.get("server"), "under_server":data.get("under_server")}).sort("cost").limit(11):
        offers.append(offer)

    await diamonds_list.cur_list.set()
    await state.update_data(cur_list = 10)
    await state.update_data(sort = "cost")

    await call.message.answer("Вот все наши предложения:",reply_markup=offers_kb(offers, 10, db))



async def diamonds_kb_pr(call:types.CallbackQuery, state:FSMContext, db:Database):
    data = await state.get_data()
    sort_by = data.get("sort")
    match call.data.replace("_offers", ""):
        case "forward":
            _cur_list = data.get("cur_list") + 10
            _offers = db["l2m"].find({"game":data.get("game"),"pr_type":data.get("game_type"), "server":data.get("server"), "under_server":data.get("under_server")}).sort(sort_by).skip(data.get("cur_list")).limit(11)
        case "back":
            _cur_list = data.get("cur_list") - 10
            if _cur_list == 10:
                _offers = db["l2m"].find({"game":data.get("game"),"pr_type":data.get("game_type"), "server":data.get("server"), "under_server":data.get("under_server")}).sort(sort_by).limit(11)
            else:
                _offers = db["l2m"].find({"game":data.get("game"),"pr_type":data.get("game_type"), "server":data.get("server"), "under_server":data.get("under_server")}).sort(sort_by).skip(_cur_list-10).limit(11)
        
        case "cost":
            _cur_list = 10
            await state.update_data(sort = "cost")
            sort_by = "cost"
            _offers = db["l2m"].find({"game":data.get("game"),"pr_type":data.get("game_type"), "server":data.get("server"), "under_server":data.get("under_server")}).sort("cost").limit(11)
        case "count":
            _cur_list = 10
            await state.update_data(sort = "name")
            sort_by = "name"
            _offers = db["l2m"].find({"game":data.get("game"),"pr_type":data.get("game_type"), "server":data.get("server"), "under_server":data.get("under_server")}).sort("name").limit(11)

        
        case "cancel":
            await state.finish()
            await call.message.delete()
            return
        
    
    offers = []
    for offer in _offers:
        offers.append(offer)
    
    await state.update_data(cur_list = _cur_list)
    await call.message.edit_reply_markup(offers_kb(offers, _cur_list, db, sort_by))


async def one_diamond_offer(call:types.CallbackQuery, state:FSMContext, db:Database):
    cur_id = ObjectId(call.data.replace("dia_offer_id:", ""))
    await state.update_data(id = cur_id)
    product = db["l2m"].find_one({"_id":cur_id})
    seller = db["users"].find_one({"telegram_id":product["seller"]})
    if call.message.chat.id == product["seller"]:
        reply_kb = diamonds_seller_kb
    else:
        reply_kb = buyer_kb
    await call.message.answer(
        "Продавец: " + str(seller["local_name"]) + "\n" +
        "Количество: " + str(product["name"]) + "\n" +
        "Цена за единицу: " + str(product["cost"]) + "\n" +
        "Комиссия: " + str(com_sw(product["comission"])) + "\n" +
        "Рейтинг: 96%\n",
        reply_markup= reply_kb
        
    )
