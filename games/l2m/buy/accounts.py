from aiogram.dispatcher import FSMContext
from aiogram import types
from pymongo.database import Database
from aiogram.dispatcher.filters.state import State, StatesGroup
from bson.objectid import ObjectId
from ..keyboards.offers.accounts_offer import offers_kb
from ..keyboards.seller_kb import seller_kb
from ..keyboards.buyer_kb import buyer_kb
from keyboards.menu import menu_kb
from ..keyboards.l2m_acc_cat import l2m_account_cat


from usefull.converters import ac_t_t

class accounts_list(StatesGroup):
    cur_list = State()
    sort = State()
    id = State()
    review_list = State()

async def accounts_out(call:types.CallbackQuery, state:FSMContext, db:Database):
    data = await state.get_data()
    offers = []
    for offer in db["l2m"].find({"game":data.get("game"),"pr_type":data.get("game_type"), "server":data.get("server"), "under_server":data.get("under_server"), "invis":False}).sort("cost").limit(11):
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

    if call.data.startswith("account_"):
        _cur_list = 10
        await state.update_data(need_c = call.data)
        _offers = db["l2m"].find({"game":data.get("game"),"pr_type":data.get("game_type"), "server":data.get("server"), "under_server":data.get("under_server"), "invis":False, "class":call.data}).sort("cost").limit(11)
        await call.message.edit_text("Вот все предложения в классе "+ac_t_t(call.data)+":")


    match call.data.replace("_offers", ""):
       
        case "forward":
            _cur_list = data.get("cur_list") + 10
            _offers = db["l2m"].find({"game":data.get("game"),"pr_type":data.get("game_type"), "server":data.get("server"), "under_server":data.get("under_server"), "invis":False}).sort(sort_by).skip(data.get("cur_list")).limit(11)
        case "back":
            _cur_list = data.get("cur_list") - 10
            if _cur_list == 10:
                _offers = db["l2m"].find({"game":data.get("game"),"pr_type":data.get("game_type"), "server":data.get("server"), "under_server":data.get("under_server"), "invis":False}).sort(sort_by).limit(11)
            else:
                _offers = db["l2m"].find({"game":data.get("game"),"pr_type":data.get("game_type"), "server":data.get("server"), "under_server":data.get("under_server"), "invis":False}).sort(sort_by).skip(_cur_list-10).limit(11)
        
        case "cost":
            _cur_list = 10
            if data.get("need_c"):
                sort_by = "c_cost"
                await state.update_data(sort = "c_cost")
                _offers = db["l2m"].find({"game":data.get("game"),"pr_type":data.get("game_type"), "server":data.get("server"), "under_server":data.get("under_server"), "invis":False, "class":data.get("need_c")}).sort("cost").limit(11)
            else:
                await state.update_data(sort = "cost")
                sort_by = "cost"
                _offers = db["l2m"].find({"game":data.get("game"),"pr_type":data.get("game_type"), "server":data.get("server"), "under_server":data.get("under_server"), "invis":False}).sort("cost").limit(11)
        case "level":
            _cur_list = 10
            
            if data.get("need_c"):
                sort_by = "c_level"
                await state.update_data(sort = "c_level")
                _offers = db["l2m"].find({"game":data.get("game"),"pr_type":data.get("game_type"), "server":data.get("server"), "under_server":data.get("under_server"), "invis":False, "class":data.get("need_c")}).sort("level").limit(11)
            else:
                sort_by = "level"
                await state.update_data(sort = "level")
                _offers = db["l2m"].find({"game":data.get("game"),"pr_type":data.get("game_type"), "server":data.get("server"), "under_server":data.get("under_server"), "invis":False}).sort("level").limit(11)
        case "class":
            await call.message.delete()
            await state.update_data(sort = "class")
            sort_by = "class"
            _cur_list = 10
            await call.message.answer("Выбери класс", reply_markup=l2m_account_cat)
            await state.update_data(cur_list = _cur_list)
            return

        
        case "cancel":
            await state.finish()
            await call.message.delete()
            return
        
    
    offers = []
    for offer in _offers:
        offers.append(offer)

    if len(offers) <= 0:
        await call.message.edit_text("В данной категории нет предложений")
    
    await state.update_data(cur_list = _cur_list)
    await call.message.edit_reply_markup(offers_kb(offers, _cur_list, db, sort_by))


async def one_account_offer(call:types.CallbackQuery, state:FSMContext, db:Database, rev = False):
    if not rev:
        cur_id = ObjectId(call.data.replace("acc_offer_id:", ""))
    else:
        data = await state.get_data()
        cur_id = data.get("id")
    await accounts_list.id.set()
    await state.update_data(id = cur_id)
    product = db["l2m"].find_one({"_id":cur_id})
    seller = db["users"].find_one({"telegram_id":product["seller"]})
    if call.message.chat.id == product["seller"]:
        reply_kb = seller_kb
    else:
        reply_kb = buyer_kb

    if seller["statistics"]["total"] >0:
        rat = seller["statistics"]["successful"] / (seller["statistics"]["total"]/100)
    else:
        rat = 0
        
    await call.message.answer(
        "Продавец: " + str(seller["local_name"]) + "\n" +
        "Класс: " + str(ac_t_t(product["class"])) + "\n" +
        "Уровень: " + str(product["level"]) + "\n" +
        "Описание: " + str(product["description"]) + "\n" +
        "Фото: " + str(product["photos"]) + "\n" +
        "Цена: " + str(product["cost"]) + "\n" +
        "Рейтинг: "+str(round(rat))+"%",
        reply_markup= reply_kb
        
    )

async def delete_accounts_offer(call:types.CallbackQuery, state:FSMContext, db:Database):
    data = await state.get_data()
    db["l2m"].delete_one({"_id":data.get("id")})
    await call.message.answer("Предложение успешно удалено")
    await accounts_out(call,state, db)

