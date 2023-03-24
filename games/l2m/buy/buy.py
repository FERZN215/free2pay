from aiogram.dispatcher import FSMContext
from aiogram import types
from pymongo.database import Database
from aiogram.dispatcher.filters.state import State, StatesGroup
from bson.objectid import ObjectId

from aiogram import Bot, Dispatcher

from keyboards.buy_start import buy_start_kb, buyer_disagree_kb
from keyboards.menu import menu_kb
from ..keyboards.no_balance import no_balance_kb
from ..keyboards.verification_kb import access_code
from usefull.acc_type_to_text import ac_t_t

from balance.b_add import balance_add_summ
from start.preview import preview
class buy_list(StatesGroup):
    buy_start = State()
    login_input = State()
    password_input = State()
    verification_code = State()
    seller_ready = State()


async def diamond_buy_process(call:types.CallbackQuery, state:FSMContext, db:Database, bot:Bot):#Для алмазов требуется отдельная функция, так как требуется указывать количество алмазов для покупки
    data = await state.get_data()
    buyer = db["users"].find_one({"telegram_id":call.message.chat.id})

    if buyer["balance"] < data.get("sum"):
        await call.message.answer("На вашем счету недостаточно средств", reply_markup=no_balance_kb)
        return
    
    db["users"].update_one({"telegram_id":call.message.chat.id}, {"$inc":{"balance":-float(data.get("sum"))}})
    db["l2m"].update_one({"_id":data.get("id")}, {"$inc":{"name":-int(data.get("buy_count"))}})

    if db["l2m"].find_one({"_id":data.get("id")})["name"] <= 0 :
        db["l2m"].delete_one({"_id":data.get("id")})

    offer = db['l2m'].find_one({"_id":data.get("id")})

    active_deal = {"status":"seller await", "game":data.get("game"), "category":data.get("game_type"), "seller":offer["seller"], "buyer":call.message.chat.id, "offer_id":data.get("id"), "count":data.get("buy_count"), "cost":data.get("sum")}
    db["active_deals"].insert_one(active_deal)
    db["users"].update_one({"telegram_id":call.message.chat.id}, {"$push":{"deals":active_deal["_id"]}})
    db["users"].update_one({"telegram_id":offer["seller"]}, {"$push":{"deals":active_deal["_id"]}})
    
    await call.message.answer("Продавцу отправлено уведомление, ожидайте", reply_markup=menu_kb)
    await bot.send_message(offer["seller"], "У вас хотят купить " + str(data.get("buy_count")) + " алмазов, по цене: " + str(offer["cost"]) + " за 1 шт\nИтого: " + str(data.get("sum"))+"\nПосле завершения вы сможете продолжить ваши дела", reply_markup=buy_start_kb(active_deal["_id"], "diamonds"))
    await state.finish()

async def diamond_seller_start(call:types.CallbackQuery, state:FSMContext, db:Database, bot:Bot):
    data_mas = call.data.partition("_buy_diamonds_start_")
    offer = db['active_deals'].find_one({"_id":ObjectId(data_mas[0])})
   
    match data_mas[2]:
        case "yes":
            await state.update_data(prev_state = await state.get_state())
            await buy_list.seller_ready.set()
            await state.update_data(cur_offer_id = ObjectId(data_mas[0]))
            db["active_deals"].update_one({"_id":ObjectId(data_mas[0])}, {"$set":{"status":"seller accepted"}})

            await bot.send_message(offer["buyer"], "Продавец принял заказ в работу, скоро придет его ответ")
            await call.message.answer("Напиши сколько лотов требуется выставить покупателю для покупки "+str(offer["count"])+" алмазов, а также их цену\nПример:\n4 лота(150, 600, 350, 100)\nЛибо:\n1 лот(1200)")

        case "later":
            await call.message.answer("Хорошо, ты сможешь продолжить данную сделку из раздела 'Активные сделки' в главном меню")
            await bot.send_message(offer["buyer"], "Продавец отложил заказ, в скором времени он может его возобновить, пока он не подтвердил заказ вы можете его отменить в разделе 'Активные сделки'")
        case "no":
            await call.message.answer("Печально")
            await bot.send_message(offer["buyer"], "Продавец отменил заказ, но ты можешь купить у других продавцов, удачи!")
            db['active_deals'].delete_one({"_id":ObjectId(data_mas[0])})
            db['users'].update_one({"telegram_id":call.message.chat.id}, {"$pull":{ObjectId(data_mas[0])}})
            db['users'].update_one({"telegram_id":offer["buyer"]}, {"$pull":{ObjectId(data_mas[0])}})

async def diamond_get_lots(message:types.Message, state:FSMContext, db:Database, bot:Bot):
    data = await state.get_data()
    offer = db["active_deals"].find_one({"_id":data.get("cur_offer_id")})
    db["active_deals"].update_one({"_id":data.get("cur_offer_id")}, {"$set":{"status":"buyer awaiting"}})
    await message.reply("Сообщение отправлено покупателю, после выкупа вами всех лотов покупатель должен подтвердить получение. Если вам кажется, что покупатель специально не подтверждает получение, то можно перейти в раздел 'Активные сделки' и попытаться решить проблему в чате, в противном случае открыть арбитраж")
    try:
        await state.set_state(data.get("prev_state"))
    except ...:
        print("no state")
    await bot.send_message(offer["buyer"],"Продавец просит выставить:\n" + message.text + "\nПосле того как продавец выкупит все лоты, <b>ОБЯЗАТЕЛЬНО</b> перейди в раздел 'Активные сделки' и подтверди получение!",parse_mode='HTML')







async def accounts_buy_process(call:types.CallbackQuery, state:FSMContext, db:Database, bot: Bot):
    # await buy_list.buy_start.set()
    data = await state.get_data()
    buyer = db["users"].find_one({"telegram_id":call.message.chat.id})
    offer = db["l2m"].find_one({"_id":data.get("id")})
    if buyer["balance"] < offer["cost"]:
        await call.message.answer("На вашем счету недостаточно средств", reply_markup=no_balance_kb)
        return
    db["users"].update_one({"telegram_id":call.message.chat.id}, {"$inc":{"balance":-float(offer["cost"])}})

    active_deal = {"status":"seller await", "game":data.get("game"), "category":data.get("game_type"), "seller":offer["seller"], "buyer":call.message.chat.id, "offer_id":data.get("id"), "cost":data.get("sum")}
    db["active_deals"].insert_one(active_deal)
    db["users"].update_one({"telegram_id":call.message.chat.id}, {"$push":{"deals":active_deal["_id"]}})
    db["users"].update_one({"telegram_id":offer["seller"]}, {"$push":{"deals":active_deal["_id"]}})
    
    await call.message.answer("Продавцу отправлено уведомление, ожидайте", reply_markup=menu_kb)
    await bot.send_message(offer["seller"], "У вас хотят купить аккаунт\nСтоимость: " + str(offer["cost"])+"\n" + game_converter(offer["game"], offer["pr_type"])+
                           "\n"+server_converter(offer["server"])+"\n"+under_server_converter(offer["under_server"])+
                           "\nКласс: "+ac_t_t(offer["class"])+"\nУровень: "+str(offer["level"])+"\nОписание: "+str(offer["description"])+
                           "\nПосле завершения вы сможете продолжить ваши дела", reply_markup=buy_start_kb(active_deal["_id"], "accounts"))
    await state.finish()




async def accounts_seller_start(call:types.CallbackQuery, state:FSMContext, db:Database, bot:Bot):
    data_mas = call.data.partition("_buy_accounts_start_")
    offer = db['active_deals'].find_one({"_id":ObjectId(data_mas[0])})
   
    match data_mas[2]:
        case "yes":
            await state.update_data(prev_state = await state.get_state())
            await buy_list.seller_ready.set()
            await state.update_data(cur_offer_id = ObjectId(data_mas[0]))
            db["active_deals"].update_one({"_id":ObjectId(data_mas[0])}, {"$set":{"status":"seller accepted"}})

            await bot.send_message(offer["buyer"], "Продавец принял заказ в работу, скоро придет его ответ")
            await call.message.answer("Напиши логин для аккаунта:")
            await buy_list.login_input.set()

        case "later":
            await call.message.answer("Хорошо, ты сможешь продолжить данную сделку из раздела 'Активные сделки' в главном меню")
            await bot.send_message(offer["buyer"], "Продавец отложил заказ, в скором времени он может его возобновить, пока он не подтвердил заказ вы можете его отменить в разделе 'Активные сделки'")
        case "no":
            await call.message.answer("Печально")
            await bot.send_message(offer["buyer"], "Продавец отменил заказ, но ты можешь купить у других продавцов, удачи!")
            db['active_deals'].delete_one({"_id":ObjectId(data_mas[0])})
            db['users'].update_one({"telegram_id":call.message.chat.id}, {"$pull":{ObjectId(data_mas[0])}})
            db['users'].update_one({"telegram_id":offer["buyer"]}, {"$pull":{ObjectId(data_mas[0])}})

  
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
        await state.set_state(data.get("prev_state"))
    except ...:
        print("no state")
    db["active_deals"].update_one({"_id": offer["_id"]}, {"$set": {"login": data.get("login")}})
    await bot.send_message(offer["buyer"],"Логин: " + data.get("login") + "\nПароль: "+ message.text + 
                           "\nПосле успешного ввода данных, вы можете запросить код подтверждения. Если же данные не действительны, вы можете обратиться к продавцу через активные сделки, пожаловаться, либо открыть арбитраж", reply_markup=access_code(offer["_id"]))

async def accounts_verification_code_awaiting(call:types.CallbackQuery, state:FSMContext, dp: Dispatcher, bot:Bot, db: Database):
    offer = db["active_deals"].find_one({"_id": ObjectId(call.data.replace("buyer_code_query:", ""))})
    await call.message.answer("Запрос отправлен продавцу")
    await dp.storage.update_data(chat = offer["seller"], data={"prev_state": await dp.storage.get_state(chat=offer["seller"]), "buyer_code_id": offer["_id"]})
    await dp.storage.set_state(chat = offer["seller"], state = buy_list.verification_code)
    await bot.send_message(offer["seller"], "Покупатель запрашивает код от аккаунта \nЛогин:" +str(offer["login"])+"\nОтправьте код, иначе покупатель будет вынужден открыть арбитраж")

async def accounts_verification_code_from_seller(message:types.Message, state:FSMContext, dp: Dispatcher, bot:Bot, db:Database):
    data = await state.get_data()
    offer = db["active_deals"].find_one({"_id": ObjectId(data.get("buyer_code_id"))})
    await bot.send_message(offer["buyer"], "Продавец отправил код от аккаунта: "+str(offer["login"])+"\nПроверьте и подтвердите выполнение сделки:\n<b>"+ message.text+"</b>", parse_mode='HTML', reply_markup=access_code(offer["_id"]))
    await state.set_state(data.get("prev_state"))

async def buy_process(call:types.CallbackQuery, state:FSMContext, db:Database):
    # await buy_list.buy_start.set()
    # data = await state.get_data()
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




def game_converter(game:str, type:str):
    match game:
        case "game_lage2m":
            match type:
                case "cat_accounts":
                    return "Игра: Lineage 2M|Тип товара: Аккаунты"
                case "cat_diamonds":
                    return "Игра: Lineage 2M|Тип товара: Алмазы"
                case "cat_things":
                    return "Игра: Lineage 2M|Тип товара: Предметы"
                case "cat_services":
                    return "Игра: Lineage 2M|Тип товара: Услуги"
                
def server_converter(server:str):
    match server:
        case "server_l2m_zighard":
            return "Сервер: Зигхард"
        case "server_l2m_barc":
            return "Сервер: Барц"
        case "server_l2m_leona":
            return "Сервер: Леона"
        case "server_l2m_erika":
            return "Сервер: Эрика" 

def under_server_converter(under_server: str):
    match under_server:
        case "under_s_l2m_1":
            return "Подсервер 1"
        case "under_s_l2m_2":
            return "Подсервер 2"
        case "under_s_l2m_3":
            return "Подсервер 3"
        case "under_s_l2m_4":
            return "Подсервер 4"
        case "under_s_l2m_5":
            return "Подсервер 5"
        case "under_s_l2m_6":
            return "Подсервер 6"         