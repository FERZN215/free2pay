from aiogram.dispatcher import FSMContext
from aiogram import types, Bot
from pymongo.database import Database
from aiogram.dispatcher.filters.state import State, StatesGroup
from bson.objectid import ObjectId
from keyboards.all_offers import all_offers_kb

from usefull.converters import *
from usefull.com_sw import com_sw

from start.personal_area import personal_area

from games.l2m.keyboards.seller_kb import seller_kb
from games.l2m.keyboards.diamond_seller_kb import diamonds_seller_kb
from games.l2m.keyboards.buyer_kb import buyer_kb
from keyboards.menu import menu_kb




class all_offers_states(StatesGroup):
    offer_list = State()
    id = State()
    new_d_count = State()

async def view_all_offers(call:types.CallbackQuery, state:FSMContext, db:Database):

    all_l2m_offers = db["l2m"].find({"seller":call.message.chat.id, "invis":False})

    offers = []
    for offer in all_l2m_offers:
        offers.append(offer)


    if len(offers) <= 0:
  
        await call.message.answer("У тебя нет товаров в продаже:", reply_markup=menu_kb)
        return

    await all_offers_states.offer_list.set()
    await state.update_data(offer_list = 10)


    await call.message.answer("Все твои предложения:", reply_markup= all_offers_kb(offers, 10))

async def all_offers_kb_manager(call:types.CallbackQuery, state:FSMContext, db:Database):
    data = await state.get_data()

    match call.data.replace("_alloffers", ""):

        case "forward":
            _cur_list = data.get("offer_list") + 10
            _offers = db["l2m"].find({"seller":call.message.chat.id, "invis":False}).skip(data.get("offer_list")).limit(11)
        case "back":
            _cur_list = data.get("offer_list") - 10
            if _cur_list == 10:
                _offers = db["l2m"].find({"seller":call.message.chat.id, "invis":False}).limit(11)
            else:
                _offers = db["l2m"].find({"seller":call.message.chat.id, "invis":False}).skip(_cur_list-10).limit(11)

        case "cancel":
            await call.message.delete()
            await state.finish()
            await personal_area(call.message, db)
            return
        
    offers = []
    for offer in _offers:
        offers.append(offer)

    
    
    await state.update_data(cur_list = _cur_list)
    await call.message.edit_reply_markup(all_offers_kb(offers, _cur_list))





async def view_one_offer(call:types.CallbackQuery, state:FSMContext, db:Database):
    offer = db["l2m"].find_one({"_id":ObjectId(call.data.replace("all_offer_id:", "")), "invis":False})
    
    match offer["pr_type"]:
        case "cat_accounts":
            await one_account_offer(call, state, db)
        case "cat_diamonds":
            await one_diamond_offer(call, state, db)
        case "cat_things":
            await one_thing_offer(call, state, db)
        case "cat_services":
            await one_service_offer(call, state, db)


async def delete_all_offer(call:types.CallbackQuery, state:FSMContext, db:Database):
    data = await state.get_data()
    
    ad = db["active_deals"].find_one({"offer_id":data.get("id")})
    if ad:
        await call.message.answer("Этот заказ уже в работе")
        await view_all_offers (call,state, db)
        return 

    db["l2m"].delete_one({"_id":data.get("id")})
    await call.message.answer("Предложение успешно удалено")
    await view_all_offers (call,state, db)

async def back_from_one_offer(call:types.CallbackQuery, state:FSMContext, db:Database):
    await view_all_offers (call,state, db)

async def change_diamond_count(call:types.CallbackQuery, state:FSMContext, db:Database):
    await all_offers_states.new_d_count.set()
    await call.message.answer("Введи новое количество алмазов:")

async def change_diamond_count_process(message:types.Message, state:FSMContext, db:Database):
    data = await state.get_data()
    if not message.text.isdigit():
        await message.answer("Количество должно быть числом, попробуй еще раз:")
        return

    db["l2m"].update_one({"_id":data.get("id")}, {"$set":{"name":int(message.text)}})
    await one_diamond_offer(message, state, db, True)




#---------------------------------------------------------------------------------------

async def one_account_offer(call:types.CallbackQuery, state:FSMContext, db:Database):

    cur_id = ObjectId(call.data.replace("all_offer_id:", ""))

    await all_offers_states.id.set()
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
        "Цена: " + str(product["cost"]) + "\n" +
        "Рейтинг: "+str(rat)+"%",
        reply_markup= reply_kb
        
    )



        
    
async def one_diamond_offer(call, state:FSMContext, db:Database, n=False):

    if n:
        data = await state.get_data()
        cur_id = data.get("id")
    else:
        cur_id = ObjectId(call.data.replace("all_offer_id:", ""))

    await all_offers_states.id.set()
    await state.update_data(id = cur_id)
    product = db["l2m"].find_one({"_id":cur_id})
    seller = db["users"].find_one({"telegram_id":product["seller"]})

    if n:
        if call.chat.id == product["seller"]:
            reply_kb = diamonds_seller_kb
        else:
            reply_kb = buyer_kb
    else:
        if call.message.chat.id == product["seller"]:
            reply_kb = diamonds_seller_kb
        else:
            reply_kb = buyer_kb

    if seller["statistics"]["total"] >0:
        rat = seller["statistics"]["successful"] / (seller["statistics"]["total"]/100)
    else:
        rat = 0



    if n:
        await call.answer(
            "Продавец: " + str(seller["local_name"]) + "\n" +
            "Количество: " + str(product["name"]) + "\n" +
            "Цена за единицу: " + str(product["cost"]) + "\n" +
            "Комиссия: " + str(com_sw(product["comission"])) + "\n" +
            "Рейтинг: "+str(rat)+"%",
            reply_markup= reply_kb
            
        )
    else:
        await call.message.answer(
            "Продавец: " + str(seller["local_name"]) + "\n" +
            "Количество: " + str(product["name"]) + "\n" +
            "Цена за единицу: " + str(product["cost"]) + "\n" +
            "Комиссия: " + str(com_sw(product["comission"])) + "\n" +
            "Рейтинг: "+str(rat)+"%",
            reply_markup= reply_kb
            
        )




async def one_thing_offer(call:types.CallbackQuery, state:FSMContext, db:Database):
  
    cur_id = ObjectId(call.data.replace("all_offer_id:", ""))

    await all_offers_states.id.set()
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
        "Тип: " + str(things_to_text(product["type"])) + "\n" +
        "Описание: " + str(product["description"]) + "\n" +
        "Цена: " + str(product["cost"]) + "\n" +
        "Рейтинг: "+str(rat)+"%",
        reply_markup= reply_kb
        
    )


async def one_service_offer(call:types.CallbackQuery, state:FSMContext, db:Database):

    cur_id = ObjectId(call.data.replace("all_offer_id:", ""))

    await all_offers_states.id.set()
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
        "Описание: " + str(product["description"]) + "\n" +
        "Цена: " + str(product["cost"]) + "\n" +
        "Рейтинг: "+str(rat)+"%",
        reply_markup= reply_kb
        
    )
