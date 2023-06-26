from aiogram.dispatcher import FSMContext
from aiogram import types
from pymongo.database import Database
from aiogram.dispatcher.filters.state import State, StatesGroup
from bson.objectid import ObjectId
from ..keyboards.offers.things_offers import offers_kb
from ..keyboards.seller_kb import seller_kb
from ..keyboards.buyer_kb import buyer_kb
from usefull.converters import things_to_text
from keyboards.menu import menu_kb
from ..keyboards.l2m_things import l2m_things_cat
from buy import *

class things_list(StatesGroup):
    cur_list = State()
    id = State()



async def things_buy_process(call:types.CallbackQuery, state:FSMContext, db:Database, bot: Bot):
  
    info = await buy_process_start_com(call, state, db)
  
    await bot.send_message(info["offer"]["seller"], "У вас хотят купить предмет\nСтоимость: " + str(info["offer"]["cost"])+"\n" + game_converter(info["offer"]["game"], info["offer"]["pr_type"])+
                           "\n"+server_converter(info["offer"]["server"])+"\n"+under_server_converter(info["offer"]["under_server"])+
                           "\nКласс: "+things_to_text(info["offer"]["type"])+"\nОписание: "+str(info["offer"]["description"])+
                           "\nПосле завершения вы сможете продолжить ваши дела", reply_markup=buy_start_kb(info["active_deal"]["_id"], "things"))
    await state.finish()





async def things_seller_start(call:types.CallbackQuery, state:FSMContext, db:Database, bot:Bot, n = False):
    if n:
        data_mas = call.data.partition("_one_")
    else:
        data_mas = call.data.partition("_buy_things_start_")
    
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
           
            await call.message.answer("Выбери тип продажи предмета:", reply_markup=thing_sell_type_kb)
            await buy_list.thing_sell_type.set()
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



async def thing_sell_type_process(call:types.CallbackQuery, state:FSMContext, db:Database, bot:Bot):
    data = await state.get_data()
    try:
        offer = db["active_deals"].find_one({"_id":ObjectId(data.get("cur_offer_id"))})
    except:
        await call.message.answer("Сделка завершена")
        return

    
    match call.data.replace("thing_sell_", ""):
        case "au":  
            await bot.send_message(offer["buyer"], "Продавец предлагает купить предмет с помошью аукциона")

            await buy_list.au_cost.set()
            await call.message.answer("Введи цену за которую ты выставишь предмет:")
        case "trade":
            await call.message.answer("Подождем подтверждения от покупателя, что он имеет 50+ уровень и 100 аламазов")
            if data.get("prev_state"):
                await state.set_state(data.get("prev_state"))
                await state.update_data(prev_state = None)
            else:
                await state.finish()
            await bot.send_message(offer["buyer"], "Продавец предлагает купить предмет с помошью трейда. Для этого вам нужно иметь 50+ уровень и 100 алмазов", reply_markup=au_buyer_kb(offer["_id"]))


async def au_cost(message:types.Message, state:FSMContext, db:Database, bot:Bot):
    data = await state.get_data()
    offer = db["active_deals"].find_one({"_id":data.get("cur_offer_id")})
    if not is_digit(message.text):
        await message.reply("Цену нужно вводить цифрой")
    if data.get("prev_state"):
        await state.set_state(data.get("prev_state"))
        await state.update_data(prev_state = None)
    else:
        await state.finish()
    db["active_deals"].update_one({"_id":data.get("cur_offer_id")}, {"$set":{"status": "buyer awaiting"}})
    await bot.send_message(offer["buyer"], "Продавец выставит предмет за цену: <b>"+message.text+"</b>"+". После того как ты выкупишь товар не забудь завершить сделку в разделе активные сделки", parse_mode='HTML')
    await message.reply("Отправлено")



async def bueyr_trade_thing(call:types.CallbackQuery, state:Database, db:Database, bot:Bot, dp:Dispatcher):
    data_mas = call.data.partition("_buyer_au_")
    try:
        offer = db["active_deals"].find_one({"_id":ObjectId(data_mas[0])})
    except:
        await call.message.answer("Заказ отменен")
    
    match data_mas[2]:
        case "dis":
            await call.message.answer("Заказ отменен")
            db["l2m"].update_one({"_id":offer["offer_id"]}, {"$set":{"invis":False}})
          
            await bot.send_message(offer["seller"], "Покупатель отменил заказ")
            
            db['active_deals'].delete_one({"_id":ObjectId(data_mas[0])})
            db['users'].update_one({"telegram_id":call.message.chat.id}, {"$pull":{"deals":ObjectId(data_mas[0])}, "$inc":{"balance":offer["cost"]}})
            db['users'].update_one({"telegram_id":offer["buyer"]}, {"$pull":{"deals":ObjectId(data_mas[0])}})
        case "accept":
            await dp.storage.update_data(chat = offer["seller"], data={"prev_state": await dp.storage.get_state(chat=offer["seller"]), "buyer_code_id": offer["_id"]})
            await dp.storage.set_state(chat = offer["seller"], state = buy_list.trade_desc)
            await bot.send_message(offer["seller"], "Покупатель подтвердил наличие нужных требований для трейда. Введи максимально подробное описание трейда(где, когда):")


async def trade_desc(message:types.Message, state:FSMContext, db:Database, bot:Bot):
    data = await state.get_data()
    offer = db["active_deals"].find_one({"_id":data.get("buyer_code_id")})
    db["active_deals"].update_one({"_id":offer["_id"]}, {"$set":{"status":"buyer awaiting"}})
    await bot.send_message(offer["buyer"], "Продавец отправил описание трейда:\n"+message.text+"\nПосле завершения трейда обязательно подтверди сделку из раздела активных сделок")
    await message.answer("Описание отправлено")
    if data.get("prev_state"):
        await state.set_state(data.get("prev_state"))
        await state.update_data(prev_state = None)
    else:
        await state.finish()


async def things_out(call:types.CallbackQuery, state:FSMContext, db:Database):
    data = await state.get_data()
    offers = []
    for offer in db["l2m"].find({"game":data.get("game"),"pr_type":data.get("game_type"), "server":data.get("server"), "under_server":data.get("under_server"), "invis":False}).sort("cost").limit(11):
        offers.append(offer)
    await things_list.cur_list.set()
    await state.update_data(cur_list = 10)
   

    if len(offers) > 0:
        await call.message.answer("Вот все наши предложения: ",reply_markup=offers_kb(offers, 10, db))
    else:
        await state.finish()
        await call.message.answer("В данном разделе отсутсвуют товары", reply_markup=menu_kb)




async def things_kb_pr(call:types.CallbackQuery, state:FSMContext, db:Database):
    data = await state.get_data()
    if call.data.startswith("things_"):
        _cur_list = 10
        _offers = db["l2m"].find({"game":data.get("game"),"pr_type":data.get("game_type"), "server":data.get("server"), "under_server":data.get("under_server"), "invis":False, "type":call.data}).sort("cost").limit(11)
        await call.message.edit_text("Вот все предложения в классе "+things_to_text(call.data)+":")


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

        case "type":
            await call.message.delete()
            _cur_list = 10
            await call.message.answer("Выбери тип", reply_markup=l2m_things_cat)
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
    await call.message.edit_reply_markup(offers_kb(offers, _cur_list, db))


async def one_thing_offer(call:types.CallbackQuery, state:FSMContext, db:Database, rev = False):
    if not rev:
        cur_id = ObjectId(call.data.replace("th_offer_id:", ""))
    else:
        data = await state.get_data()
        cur_id = data.get("id")


    await things_list.id.set()
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
        "Рейтинг: "+str(round(rat))+"%",
        reply_markup= reply_kb
        
    )

async def delete_things_offer(call:types.CallbackQuery, state:FSMContext, db:Database):
    data = await state.get_data()
    db["l2m"].delete_one({"_id":data.get("id")})
    await call.message.answer("Предложение успешно удалено")
    await things_out(call,state, db)