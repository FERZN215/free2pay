from aiogram.dispatcher import FSMContext
from aiogram import types
from pymongo.database import Database
from aiogram.dispatcher.filters.state import State, StatesGroup
from bson.objectid import ObjectId
from ..keyboards.offers.diamond_offers import offers_kb
from usefull.com_sw import com_sw
from ..keyboards.diamond_seller_kb import diamonds_seller_kb
from ..keyboards.buyer_kb import buyer_kb
from ..keyboards.diamonds_buy import diamond_buy_kb
from keyboards.menu import menu_kb

class diamonds_list(StatesGroup):
    cur_list = State()
    sort = State()
    id = State()

    buy_count = State()
    sum = State()


async def diamonds_out(call:types.CallbackQuery, state:FSMContext, db:Database):
    data = await state.get_data()
    offers = []
    for offer in db["l2m"].find({"game":data.get("game"),"pr_type":data.get("game_type"), "server":data.get("server"), "under_server":data.get("under_server")}).sort("cost").limit(11):
        offers.append(offer)

    await diamonds_list.cur_list.set()
    await state.update_data(cur_list = 10)
    await state.update_data(sort = "cost")

    if len(offers) > 0:
        await call.message.answer("Вот все наши предложения: ",reply_markup=offers_kb(offers, 10, db))
    else:
        await state.finish()
        await call.message.answer("В данном разделе отсутсвуют товары", reply_markup=menu_kb)




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


async def one_diamond_offer(call=None, state=None, db=None, msg = None):
    if msg == None:
        cur_id = ObjectId(call.data.replace("dia_offer_id:", ""))
        await state.update_data(id = cur_id)
    else:
        data = await state.get_data()
        cur_id = data.get("id")

    product = db["l2m"].find_one({"_id":cur_id})
    seller = db["users"].find_one({"telegram_id":product["seller"]})


    if msg == None:
        if call.message.chat.id == product["seller"]:
            reply_kb = diamonds_seller_kb
        else:
            reply_kb = buyer_kb
    else:
        if msg.chat.id == product["seller"]:
            reply_kb = diamonds_seller_kb
        else:
            reply_kb = buyer_kb

    if msg == None:
        await call.message.answer(
            "Продавец: " + str(seller["local_name"]) + "\n" +
            "Количество: " + str(product["name"]) + "\n" +
            "Цена за единицу: " + str(product["cost"]) + "\n" +
            "Комиссия: " + str(com_sw(product["comission"])) + "\n" +
            "Рейтинг: 96%\n",
            reply_markup= reply_kb
            
        )
    else:
        await msg.answer(
            "Продавец: " + str(seller["local_name"]) + "\n" +
            "Количество: " + str(product["name"]) + "\n" +
            "Цена за единицу: " + str(product["cost"]) + "\n" +
            "Комиссия: " + str(com_sw(product["comission"])) + "\n" +
            "Рейтинг: 96%\n",
            reply_markup= reply_kb
            
        )


async def buy_diamonds_start(call:types.CallbackQuery, state:FSMContext):
    await diamonds_list.buy_count.set()
    await call.message.answer("Введите желаемое количество алмазов:")
    
async def diamonds_count_process(message:types.Message, state:FSMContext, db:Database):
    data = await state.get_data()
    product = db["l2m"].find_one({"_id":data.get("id")})
    
    if message.text.isdigit() == False:
        await message.reply("Количество должно быть указано целым числом, повтори попытку")
        return
    if int(message.text) > product["name"]:
        await message.reply("У данной позиции нет такого количества алмазов, повтори попытку")
        return
    await diamonds_list.sum.set()
    await state.update_data(buy_count = int(message.text), sum = product["cost"] * int(message.text))
    await message.answer("Итоговая стоимость составит " + str(product["cost"] * int(message.text)), reply_markup=diamond_buy_kb)







#-------------------------seller------------------------
async def delete_diamond_offer(call:types.CallbackQuery, state:FSMContext, db:Database):
    data = await state.get_data()
    db["l2m"].delete_one({"_id":data.get("id")})
    await call.message.answer("Предложение успешно удалено")
    await diamonds_out(call,state, db)


async def change_diamond_count_start(call:types.CallbackQuery, state:FSMContext):
    await call.message.answer("Введи новое количество алмазов:")

async def change_diamond_count_process(message:types.Message, state:FSMContext, db:Database):
    if message.text.isdigit() == False:
        await message.reply("Количество должно быть указано целым числом, повтори попытку")
        return
    data = await state.get_data()
    db["l2m"].update_one({"_id":data.get("id")}, {"$set":{"name":int(message.text)}})
    await one_diamond_offer(state=state, db=db, msg=message)



