from aiogram.dispatcher import FSMContext
from aiogram import types
from pymongo.database import Database
from aiogram.dispatcher.filters.state import State, StatesGroup
from bson.objectid import ObjectId

from aiogram import Bot, Dispatcher

from keyboards.buy_start import buy_start_kb, buyer_disagree_kb
from keyboards.menu import menu_kb
from ..keyboards.no_balance import no_balance_kb

from balance.b_add import balance_add_summ
from start.preview import preview
class buy_list(StatesGroup):
    buy_start = State()
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
    await bot.send_message(offer["seller"], "У вас хотят купить " + str(data.get("buy_count")) + " алмазов, по цене: " + str(offer["cost"]) + " за 1 шт\nИтого: " + str(data.get("sum"))+"\nПосле завершения вы сможете продолжить ваши дела", reply_markup=buy_start_kb(active_deal["_id"]))
    await state.finish()

async def diamond_seller_start(call:types.CallbackQuery, state:FSMContext, db:Database, bot:Bot):
    data_mas = call.data.partition("_buy_start_")
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







async def accounts_buy_process(call:types.CallbackQuery, state:FSMContext, db:Database):
    await buy_list.buy_start.set()
    data = await state.get_data()
    buyer = db["users"].find_one({"telegram_id":call.message.chat.id})
    offer = db["l2m"].find_one({"_id":data.get("id")})
    if buyer["balance"] < offer["cost"]:
        await call.message.answer("На вашем счету недостаточно средств", reply_markup=no_balance_kb)
        return
    db["users"].update_one({"telegram_id":call.message.chat.id}, {"$inc":{"balance":-float(offer["cost"])}})

  


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