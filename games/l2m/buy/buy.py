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

async def diamond_buy_process(call:types.CallbackQuery, state:FSMContext, db:Database, bot:Bot):#Для алмазов требуется отдельная функция, так как требуется указывать количество алмазов для покупки
    data = await state.get_data()
    buyer = db["users"].find_one({"telegram_id":call.message.chat.id})
    
    if buyer["balance"] < data.get("sum"):
        await call.message.answer("На вашем счету недостаточно средств", reply_markup=no_balance_kb)
        return
    db["l2m"].update_one({"_id":data.get("id")}, {"$set":{"invis":True}})
    db["users"].update_one({"telegram_id":call.message.chat.id}, {"$inc":{"balance":-float(data.get("sum"))}})

    # if db["l2m"].find_one({"_id":data.get("id")})["name"] <= 0 :
    #     db["l2m"].delete_one({"_id":data.get("id")})

    offer = db['l2m'].find_one({"_id":data.get("id")})

    active_deal = {"status":"seller await", "game":data.get("game"), "category":data.get("game_type"), "seller":offer["seller"], "buyer":call.message.chat.id, "offer_id":data.get("id"), "count":data.get("buy_count"), "cost":data.get("sum")}
    db["active_deals"].insert_one(active_deal)
    db["users"].update_one({"telegram_id":call.message.chat.id}, {"$push":{"deals":active_deal["_id"]}})
    db["users"].update_one({"telegram_id":offer["seller"]}, {"$push":{"deals":active_deal["_id"]}})
    
    await call.message.answer("Продавцу отправлено уведомление, ожидайте", reply_markup=menu_kb)
    await bot.send_message(offer["seller"], "У вас хотят купить " + str(data.get("buy_count")) + " алмазов, по цене: " + str(offer["cost"]) + " за 1 шт\nИтого: " + str(data.get("sum"))+"\nПосле завершения вы сможете продолжить ваши дела", reply_markup=buy_start_kb(active_deal["_id"], "diamonds"))
    await state.finish()

async def diamond_seller_start(call:types.CallbackQuery, state:FSMContext, db:Database, bot:Bot, n = False):
    if n:
        data_mas = call.data.partition("_one_")
    else:
        data_mas = call.data.partition("_buy_diamonds_start_")
    try:    
        offer = db['active_deals'].find_one({"_id":ObjectId(data_mas[0])})
    except TypeError:
        await call.message.answer("Заказ отменен")
        return
    
    match data_mas[2]:
        case "yes":
            if not n:
                await state.update_data(prev_state = await state.get_state())

            await buy_list.seller_ready.set()
            await state.update_data(cur_offer_id = ObjectId(data_mas[0]))

            db["l2m"].update_one({"_id":offer["offer_id"]}, {"$inc":{"name":-int(offer["count"])}})
            db["active_deals"].update_one({"_id":ObjectId(data_mas[0])}, {"$set":{"status":"seller accepted"}})
            db["users"].update_one({"telegram_id":call.message.chat.id}, {"$inc":{"statistics.total":1}})
            await bot.send_message(offer["buyer"], "Продавец принял заказ в работу, скоро придет его ответ")
            await call.message.answer("Напиши сколько лотов требуется выставить покупателю для покупки "+str(offer["count"])+" алмазов, а также их цену\nПример:\n4 лота(150, 600, 350, 100)\nЛибо:\n1 лот(1200)")

        case "later":
            await call.message.answer("Хорошо, ты сможешь продолжить данную сделку из раздела 'Активные сделки' в главном меню")
            await bot.send_message(offer["buyer"], "Продавец отложил заказ, в скором времени он может его возобновить, пока он не подтвердил заказ вы можете его отменить в разделе 'Активные сделки'")
        
        case "no":
            db["l2m"].update_one({"_id":offer["offer_id"]}, {"$set":{"invis":False}})
            await call.message.answer("Печально")
            await bot.send_message(offer["buyer"], "Продавец отменил заказ, но ты можешь купить у других продавцов, удачи!")
            db['active_deals'].delete_one({"_id":ObjectId(data_mas[0])})
            db['users'].update_one({"telegram_id":call.message.chat.id}, {"$pull":{"deals":ObjectId(data_mas[0])}})
            db['users'].update_one({"telegram_id":offer["buyer"]}, {"$pull":{"deals":ObjectId(data_mas[0])} , "$inc":{"balance":float(offer["cost"])}})

async def diamond_get_lots(message:types.Message, state:FSMContext, db:Database, bot:Bot):
    data = await state.get_data()
    offer = db["active_deals"].find_one({"_id":data.get("cur_offer_id")})
    db["active_deals"].update_one({"_id":data.get("cur_offer_id")}, {"$set":{"status":"buyer awaiting"}})
    await message.reply("Сообщение отправлено покупателю, после выкупа вами всех лотов покупатель должен подтвердить получение. Если вам кажется, что покупатель специально не подтверждает получение, то можно перейти в раздел 'Активные сделки' и попытаться решить проблему в чате, в противном случае открыть арбитраж")
    try:
        if data.get("prev_state"):
            await state.set_state(data.get("prev_state"))
            await state.update_data(prev_state = None)
        else:
            await state.finish()
    except:
        print("no state")
    await bot.send_message(offer["buyer"],"Продавец просит выставить:\n" + message.text + "\nПосле того как продавец выкупит все лоты, <b>ОБЯЗАТЕЛЬНО</b> перейди в раздел 'Активные сделки' и подтверди получение!",parse_mode='HTML')




#------------------------------------------------------------------------------------------------------------------------------------------------------



async def accounts_buy_process(call:types.CallbackQuery, state:FSMContext, db:Database, bot: Bot):
    info = await buy_process_start_com(call, state, db)
    

    await bot.send_message(info["offer"]["seller"], "У вас хотят купить аккаунт\nСтоимость: " + str(info["offer"]["cost"])+"\n" + game_converter(info["offer"]["game"], info["offer"]["pr_type"])+
                           "\n"+server_converter(info["offer"]["server"])+"\n"+under_server_converter(info["offer"]["under_server"])+
                           "\nКласс: "+ac_t_t(info["offer"]["class"])+"\nУровень: "+str(info["offer"]["level"])+"\nОписание: "+str(info["offer"]["description"])+
                           "\nПосле завершения вы сможете продолжить ваши дела", reply_markup=buy_start_kb(info["active_deal"]["_id"], "accounts"))
    await state.finish()

async def accounts_seller_start(call:types.CallbackQuery, state:FSMContext, db:Database, bot:Bot, n = False):
    if n:
        data_mas = call.data.partition("_one_")
    else:
        data_mas = call.data.partition("_buy_accounts_start_")
    
    try:
        offer = db['active_deals'].find_one({"_id":ObjectId(data_mas[0])})
    except TypeError:
        await call.message.answer("Заказ отменен")
        return
    
    if await state.get_state() == "buy_list:login_input":
        await call.message.answer("SMTH went wrong")
        return
    
    if offer["status"] == "buyer awaiting":
        await call.message.answer("SMTH went wrong")
        return


    match data_mas[2]:
        case "yes":
            if not n:
                
                await state.update_data(prev_state = await state.get_state())

            
            await state.update_data(cur_offer_id = ObjectId(data_mas[0]))
            db["active_deals"].update_one({"_id":ObjectId(data_mas[0])}, {"$set":{"status":"seller accepted"}})
            db["users"].update_one({"telegram_id":call.message.chat.id}, {"$inc":{"statistics.total":1}})
            await bot.send_message(offer["buyer"], "Продавец принял заказ в работу, скоро придет его ответ")
            await call.message.answer("Напиши логин для аккаунта:")
            await buy_list.login_input.set()
        case "later":
            await call.message.answer("Хорошо, ты сможешь продолжить данную сделку из раздела 'Активные сделки' в главном меню")
            await bot.send_message(offer["buyer"], "Продавец отложил заказ, в скором времени он может его возобновить, пока он не подтвердил заказ вы можете его отменить в разделе 'Активные сделки'")
        case "no":
            db["l2m"].update_one({"_id":offer["offer_id"]}, {"$set":{"invis":False}})
            await call.message.answer("Печально")
            await bot.send_message(offer["buyer"], "Продавец отменил заказ, но ты можешь купить у других продавцов, удачи!")
            
            db['active_deals'].delete_one({"_id":ObjectId(data_mas[0])})
            db['users'].update_one({"telegram_id":call.message.chat.id}, {"$pull":{"deals":ObjectId(data_mas[0])}, "$inc":{"balance":offer["cost"]}})
            db['users'].update_one({"telegram_id":offer["buyer"]}, {"$pull":{"deals":ObjectId(data_mas[0])}})
  
async def accounts_get_login(message:types.Message, state:FSMContext):
    await state.update_data(login = message.text)
    await message.reply("Теперь введи пароль от него")
    await buy_list.password_input.set()

async def accounts_get_password(message:types.Message, state:FSMContext, db:Database, bot:Bot):
    data = await state.get_data()
    offer = db["active_deals"].find_one({"_id":data.get("cur_offer_id")})
    db["active_deals"].update_one({"_id":data.get("cur_offer_id")}, {"$set":{"status":"buyer awaiting"}})
    await message.reply("Данные отправлены покупателю. Если вам кажется, что покупатель специально не подтверждает получение, то можно перейти в раздел 'Активные сделки' и попытаться решить проблему в чате, в противном случае открыть арбитраж")
    try:
        if data.get("prev_state"):
            await state.set_state(data.get("prev_state"))
            await state.update_data(prev_state = None)
        else:
            await state.finish()
    except:
        print("no state")
    db["active_deals"].update_one({"_id": offer["_id"]}, {"$set": {"login": data.get("login")}})
    await bot.send_message(offer["buyer"],"Логин: " + data.get("login") + "\nПароль: "+ message.text + 
                           "\nПосле успешного ввода данных, вы можете запросить код подтверждения. Если же данные не действительны, вы можете обратиться к продавцу через активные сделки, пожаловаться, либо открыть арбитраж", reply_markup=access_code(offer["_id"]))

async def accounts_verification_code_awaiting(call:types.CallbackQuery, state:FSMContext, dp: Dispatcher, bot:Bot, db: Database):
    
    try:
        offer = db["active_deals"].find_one({"_id": ObjectId(call.data.replace("buyer_code_query:", ""))})
    except:
        await call.message.answer("Заказ заверешен")

    if offer["status"] != "buyer awaiting":
        await call.message.answer("Самса вентиль врог")
        return

    if await dp.storage.get_state(chat=offer["seller"]) == buy_list.verification_code:
        await call.message.reply("Повтори попытку немного попозже, продавец отправляет код другому покупателю", reply_markup=access_code(offer["_id"]))
        return

    await call.message.answer("Запрос отправлен продавцу")
    await dp.storage.update_data(chat = offer["seller"], data={"prev_state": await dp.storage.get_state(chat=offer["seller"]), "buyer_code_id": offer["_id"]})
    await dp.storage.set_state(chat = offer["seller"], state = buy_list.verification_code)
    await bot.send_message(offer["seller"], "Покупатель запрашивает код от аккаунта \nЛогин:" +str(offer["login"])+"\nОтправьте код, иначе покупатель будет вынужден открыть арбитраж")

async def accounts_verification_code_from_seller(message:types.Message, state:FSMContext, dp: Dispatcher, bot:Bot, db:Database):
    data = await state.get_data()
    await message.reply("Отправлено")
    offer = db["active_deals"].find_one({"_id": ObjectId(data.get("buyer_code_id"))})
    await bot.send_message(offer["buyer"], "Продавец отправил код от аккаунта: "+str(offer["login"])+"\nПроверьте и подтвердите выполнение сделки:\n<b>"+ message.text+"</b>", parse_mode='HTML', reply_markup=access_code(offer["_id"]))
    if data.get("prev_state"):
        await state.set_state(data.get("prev_state"))
        await state.update_data(prev_state = None)
    else:
        await state.finish()

#------------------------------------------------------------------------------------------------------------------------------------------------------



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


# ----------------------------------------------------------------------------------------------------------------------------------------

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



