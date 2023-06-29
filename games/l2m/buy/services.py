from aiogram.dispatcher import FSMContext
from aiogram import types
from pymongo.database import Database
from aiogram.dispatcher.filters.state import State, StatesGroup
from bson.objectid import ObjectId
from ..keyboards.offers.services_offer import offers_kb
from ..keyboards.seller_kb import seller_kb
from ..keyboards.buyer_kb import buyer_kb
from keyboards.menu import menu_kb
from .buy import *
from usefull.list_in_app import web_kb

class services_list(StatesGroup):
    cur_list = State()
    id = State()

async def services_out(call:types.CallbackQuery, state:FSMContext, db:Database):
    data = await state.get_data()
    offers = []
    for offer in db["l2m"].find({"game":data.get("game"),"pr_type":data.get("game_type"), "server":data.get("server"), "under_server":data.get("under_server"), "invis":False}).sort("cost").limit(11):
        offers.append(offer)

    await services_list.cur_list.set()
    await state.update_data(cur_list = 10)
   

    if len(offers) > 0:
        await call.message.answer("Вот все наши предложения: ",reply_markup=web_kb(data))
    else:
        await state.finish()
        await call.message.answer("В данном разделе отсутсвуют товары", reply_markup=menu_kb)


# ----------------------------------------------------------------------------------------------------------------------------------------




async def services_buy_process(call:types.CallbackQuery, state:FSMContext, db:Database, bot: Bot):
    info = await buy_process_start_com(call, state, db)
    

    await bot.send_message(info["offer"]["seller"], "У вас хотят заказать услугу\nСтоимость: " + str(info["offer"]["cost"])+"\n" + game_converter(info["offer"]["game"], info["offer"]["pr_type"])+"\n"+server_converter(info["offer"]["server"])+"\n"+under_server_converter(info["offer"]["under_server"])+"\nНазвание: "+str(info["offer"]["name"])+"\nОписание: "+str(info["offer"]["description"])+"\nПосле завершения вы сможете продолжить ваши дела", reply_markup=buy_start_kb(info["active_deal"]["_id"], "services"))
    await state.finish()

async def services_seller_start(call:types.CallbackQuery, state:FSMContext, db:Database, bot:Bot, n = False):
    if n:
        data_mas = call.data.partition("_one_")
    else:
        data_mas = call.data.partition("_buy_services_start_")
    
    try:
        offer = db['active_deals'].find_one({"_id":ObjectId(data_mas[0])})
    except TypeError:
        await call.message.answer("Заказ отменен")
        return

    match data_mas[2]:
        case "yes":
            if not n:
                await state.update_data(prev_state = await state.get_state())

            
            await state.update_data(cur_offer_id = ObjectId(data_mas[0]))
            db["active_deals"].update_one({"_id":ObjectId(data_mas[0])}, {"$set":{"status":"seller accepted"}})
            await bot.send_message(offer["buyer"], "Продавец принял заказ в работу, скоро придет его ответ")
            db["users"].update_one({"telegram_id":call.message.chat.id}, {"$inc":{"statistics.total":1}})
            await call.message.answer("Напишите подробно об услуге и инструкцию покупателю, которую вы можете предоставить:")
            await buy_list.service_instruction.set()
        case "later":
            await call.message.answer("Хорошо, ты сможешь продолжить данную сделку из раздела 'Активные сделки' в главном меню")
            await bot.send_message(offer["buyer"], "Продавец отложил заказ, в скором времени он может его возобновить, пока он не подтвердил заказ вы можете его отменить в разделе 'Активные сделки'")
        case "no":
            db["l2m"].update_one({"_id":offer["offer_id"]}, {"$set":{"invis":False}})
            await call.message.answer("Печально")
            await bot.send_message(offer["buyer"], "Продавец отменил заказ, но ты можешь купить у других продавцов, удачи!")
            db['active_deals'].delete_one({"_id": ObjectId(data_mas[0])})
            db['users'].update_one({"telegram_id":call.message.chat.id}, {"$pull":{"deals":ObjectId(data_mas[0])}})
            db['users'].update_one({"telegram_id":offer["buyer"]}, {"$pull":{"deals":ObjectId(data_mas[0])}})
            db['users'].update_one({"telegram_id":offer["buyer"]}, {"$inc":{"balance":offer["cost"]}})




async def services_get_instruction(message:types.Message, state:FSMContext, db:Database, bot:Bot):
    data = await state.get_data()
    offer = db["active_deals"].find_one({"_id":data.get("cur_offer_id")})
    db["active_deals"].update_one({"_id":data.get("cur_offer_id")}, {"$set":{"status":"buyer awaiting"}})
    await message.reply("Инструкции отправлены покупателю. Если вам кажется, что покупатель специально не подтверждает получение, то можно перейти в раздел 'Активные сделки' и попытаться решить проблему в чате, в противном случае открыть арбитраж")
    try:
        if data.get("prev_state"):
            await state.set_state(data.get("prev_state"))
            await state.update_data(prev_state = None)
        else:
            await state.finish()
    except:
        print("no state")
    db["active_deals"].update_one({"_id": offer["_id"]}, {"$set": {"instruction": message.text}})
    await bot.send_message(offer["buyer"],"Инструкция от продавца: " + message.text + 
                           "\nЕсли у вас остались вопросы, вы можете связаться с покупателем через чат и Активные сделки.\nЕсли вы заметите нарушения, у вас есть возможность пожаловаться и открыть арбитраж", reply_markup=service_access(offer["_id"]))

#----------------------------------------

async def services_kb_pr(call:types.CallbackQuery, state:FSMContext, db:Database):
    data = await state.get_data()
    match call.data.replace("_offers", ""):
        case "forward":
            _cur_list = data.get("cur_list") + 10
            _offers = db["l2m"].find({"game":data.get("game"),"pr_type":data.get("game_type"), "server":data.get("server"), "under_server":data.get("under_server"), "invis":False}).sort("cost").skip(data.get("cur_list")).limit(11)
        case "back":
            _cur_list = data.get("cur_list") - 10
            if _cur_list == 10:
                _offers = db["l2m"].find({"game":data.get("game"),"pr_type":data.get("game_type"), "server":data.get("server"), "under_server":data.get("under_server"), "invis":False}).sort("cost").limit(11)
            else:
                _offers = db["l2m"].find({"game":data.get("game"),"pr_type":data.get("game_type"), "server":data.get("server"), "under_server":data.get("under_server"), "invis":False}).sort("cost").skip(_cur_list-10).limit(11)

        case "cancel":
            await state.finish()
            await call.message.delete()
            return
        
    
    offers = []
    for offer in _offers:
        offers.append(offer)
    
    await state.update_data(cur_list = _cur_list)
    await call.message.edit_reply_markup(offers_kb(offers, _cur_list, db))


async def one_service_offer(call:types.CallbackQuery, state:FSMContext, db:Database, rev = False):
    if not rev:
        cur_id = ObjectId(call.data.replace("ser_offer_id:", ""))
    else:
        data = await state.get_data()
        cur_id = data.get("id")
        
    await services_list.id.set()
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
        "Рейтинг: "+str(round(rat))+"%",
        reply_markup= reply_kb
        
    )

async def delete_services_offer(call:types.CallbackQuery, state:FSMContext, db:Database):
    data = await state.get_data()
    db["l2m"].delete_one({"_id":data.get("id")})
    await call.message.answer("Предложение успешно удалено")
    await services_out(call,state, db)
