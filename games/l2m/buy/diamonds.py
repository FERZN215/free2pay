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
from buy import *

class diamonds_list(StatesGroup):
    cur_list = State()
    sort = State()
    id = State()

    buy_count = State()
    sum = State()


async def diamonds_out(call:types.CallbackQuery, state:FSMContext, db:Database):
    data = await state.get_data()
    offers = []
    for offer in db["l2m"].find({"game":data.get("game"),"pr_type":data.get("game_type"), "server":data.get("server"), "under_server":data.get("under_server"), "invis":False}).sort("cost").limit(11):
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
            _offers = db["l2m"].find({"game":data.get("game"),"pr_type":data.get("game_type"), "server":data.get("server"), "under_server":data.get("under_server"), "invis":False}).sort(sort_by).skip(data.get("cur_list")).limit(11)
        case "back":
            _cur_list = data.get("cur_list") - 10
            if _cur_list == 10:
                _offers = db["l2m"].find({"game":data.get("game"),"pr_type":data.get("game_type"), "server":data.get("server"), "under_server":data.get("under_server"), "invis":False}).sort(sort_by).limit(11)
            else:
                _offers = db["l2m"].find({"game":data.get("game"),"pr_type":data.get("game_type"), "server":data.get("server"), "under_server":data.get("under_server"), "invis":False}).sort(sort_by).skip(_cur_list-10).limit(11)
        
        case "cost":
            _cur_list = 10
            await state.update_data(sort = "cost")
            sort_by = "cost"
            _offers = db["l2m"].find({"game":data.get("game"),"pr_type":data.get("game_type"), "server":data.get("server"), "under_server":data.get("under_server"), "invis":False}).sort("cost").limit(11)
        case "count":
            _cur_list = 10
            await state.update_data(sort = "name")
            sort_by = "name"
            _offers = db["l2m"].find({"game":data.get("game"),"pr_type":data.get("game_type"), "server":data.get("server"), "under_server":data.get("under_server"), "invis":False}).sort("name").limit(11)

        
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

    await diamonds_list.id.set()
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

    if seller["statistics"]["total"] >0:
        rat = seller["statistics"]["successful"] / (seller["statistics"]["total"]/100)
    else:
        rat = 0

    if msg == None:
        await call.message.answer(
            "Продавец: " + str(seller["local_name"]) + "\n" +
            "Количество: " + str(product["name"]) + "\n" +
            "Цена за единицу: " + str(product["cost"]) + "\n" +
            "Комиссия: " + str(com_sw(product["comission"])) + "\n" +
            "Рейтинг: "+str(round(rat))+"%",
            reply_markup= reply_kb
            
        )
    else:
        await msg.answer(
            "Продавец: " + str(seller["local_name"]) + "\n" +
            "Количество: " + str(product["name"]) + "\n" +
            "Цена за единицу: " + str(product["cost"]) + "\n" +
            "Комиссия: " + str(com_sw(product["comission"])) + "\n" +
            "Рейтинг: "+str(round(rat))+"%",
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



#from buy process

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



