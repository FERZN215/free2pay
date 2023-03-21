from aiogram.dispatcher import FSMContext
from aiogram import types
from pymongo.database import Database
from aiogram.dispatcher.filters.state import State, StatesGroup
from bson.objectid import ObjectId
from ..keyboards.offers.accounts_offer import offers_kb
from ..keyboards.seller_kb import seller_kb
from ..keyboards.buyer_kb import buyer_kb
from keyboards.menu import menu_kb

from usefull.acc_type_to_text import ac_t_t

class accounts_list(StatesGroup):
    cur_list = State()
    sort = State()
    id = State()

async def accounts_out(call:types.CallbackQuery, state:FSMContext, db:Database):
    data = await state.get_data()
    offers = []
    for offer in db["l2m"].find({"game":data.get("game"),"pr_type":data.get("game_type"), "server":data.get("server"), "under_server":data.get("under_server")}).sort("cost").limit(11):
        offers.append(offer)


    await accounts_list.cur_list.set()
    await state.update_data(cur_list = 10)
    await state.update_data(sort = "cost")

    if len(offers) > 0:
        await call.message.answer("Вот все наши предложения: ",reply_markup=offers_kb(offers, 10, db))
    else:
        await state.finish()
        await call.message.answer("В данном разделе отсутсвуют товары", reply_markup=menu_kb)


async def account_kb_pr(call:types.CallbackQuery, state:FSMContext, db:Database):
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
        case "level":
            _cur_list = 10
            await state.update_data(sort = "level")
            sort_by = "level"
            _offers = db["l2m"].find({"game":data.get("game"),"pr_type":data.get("game_type"), "server":data.get("server"), "under_server":data.get("under_server")}).sort("level").limit(11)

        
        case "cancel":
            await state.finish()
            await call.message.delete()
            return
        
    
    offers = []
    for offer in _offers:
        offers.append(offer)
    
    await state.update_data(cur_list = _cur_list)
    await call.message.edit_reply_markup(offers_kb(offers, _cur_list, db, sort_by))


async def one_account_offer(call:types.CallbackQuery, state:FSMContext, db:Database):
    cur_id = ObjectId(call.data.replace("acc_offer_id:", ""))
    await accounts_list.id.set()
    await state.update_data(id = cur_id)
    product = db["l2m"].find_one({"_id":cur_id})
    seller = db["users"].find_one({"telegram_id":product["seller"]})
    if call.message.chat.id == product["seller"]:
        reply_kb = seller_kb
    else:
        reply_kb = buyer_kb
    await call.message.answer(
        "Продавец: " + str(seller["local_name"]) + "\n" +
        "Класс: " + str(ac_t_t(product["class"])) + "\n" +
        "Уровень: " + str(product["level"]) + "\n" +
        "Цена: " + str(product["cost"]) + "\n" +
        "Рейтинг: 96%\n",
        reply_markup= reply_kb
        
    )
