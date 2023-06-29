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
from .buy import *
from usefull.list_in_app import web_kb

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
    # тут можно дату передавать в юзфул функцию
    if len(offers) > 0:
        await call.message.answer("Вот все наши предложения: ",reply_markup=web_kb(data))
    else:
        await state.finish()
        await call.message.answer("В данном разделе отсутсвуют товары", reply_markup=menu_kb)


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
#----------------------------------------------------------------------------------------------------------------


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

