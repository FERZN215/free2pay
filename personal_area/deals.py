from aiogram.dispatcher import FSMContext
from aiogram import types, Bot
from pymongo.database import Database
from aiogram.dispatcher.filters.state import State, StatesGroup
from keyboards.deals_kb import active_deals_kb, converter, status, one_active_deal_kb_buyer, one_active_deal_kb_seller
from bson.objectid import ObjectId
from games.l2m.buy.buy import diamond_seller_start, accounts_seller_start, things_seller_start
from keyboards.menu import menu_kb

class active_deals_list(StatesGroup):
    deal_list = State()
    id = State()

async def deals_process(message:types.Message, state:FSMContext, db:Database):

    await active_deals_list.deal_list.set() 
    await state.update_data(deal_list = 10)

    user = db["users"].find_one({"telegram_id":message.chat.id})

    if len(user["deals"]) <=0:
        await message.answer("У вас нет активных сделок(", reply_markup=menu_kb)
        await state.finish()
        return
    
    await message.answer("Активные сделки:", reply_markup=active_deals_kb(user["deals"][:11], 10, message.chat.id, db))



async def deals_kb_process(call:types.CallbackQuery, state:FSMContext, db:Database):
    data = await state.get_data()
    user = db["users"].find_one({"telegram_id": call.message.chat.id})
    match call.data.replace("_deals", ""):
        case "forward":
            _cur_list = data.get("deal_list") + 10
            _deals = user["deals"][data.get("deal_list"): _cur_list+1]
            
        case "back":
            _cur_list = data.get("deal_list") - 10
            _deals = user["deals"][_cur_list-10:_cur_list+1]

        case "cancel":
            await call.message.delete()
            await state.finish()
            return
        
    await state.update_data(deal_list = _cur_list)
    await call.message.edit_reply_markup(active_deals_kb(_deals, _cur_list, call.message.chat.id, db))

async def one_active_deal(call:types.CallbackQuery, state:FSMContext, db:Database):
    try:
        deal = db["active_deals"].find_one({"_id":ObjectId(call.data.replace("active_deal_id:", ""))})
    except TypeError:
        await call.message.answer("Заказ отменен")
        await deals_process(call.message, state, db)
        return
    
    buyer = db["users"].find_one({"telegram_id":deal["buyer"]})
    seller = db["users"].find_one({"telegram_id":deal["seller"]})
    if call.message.chat.id == buyer["telegram_id"]:
        need_kb = one_active_deal_kb_buyer(deal["status"], deal["_id"])
    else:
        need_kb = one_active_deal_kb_seller(deal["status"], deal["_id"])
    await active_deals_list.id.set()
    await call.message.answer(
        converter(deal["game"], deal["category"]) + "\n" +
        "Продавец: " + seller["local_name"] +"\n"+
        "Покупатель: " + buyer["local_name"] +"\n"+
        "Статус: " + status(deal["status"]) +"\n"+
        "Цена: "+ str(deal["cost"]),reply_markup=need_kb
                        )
    

async def manage_deal(call:types.CallbackQuery, state:FSMContext, db:Database, bot:Bot):
    data_mas = call.data.partition("_one_")
    try:
        offer = db['active_deals'].find_one({"_id":ObjectId(data_mas[0])})
    except TypeError:
        await call.message.answer("Заказ отменен")
        await deals_process(call.message, state, db)
        return


    match offer["game"]:

        case "game_lage2m":

            match offer["category"]:

                case"cat_diamonds":


                    match data_mas[2]:
                        
                        case "yes" | "no":
                           await diamond_seller_start(call, state, db, bot, True)
                            
                        case "buyer_no":
                            if offer["status"] == "seller await":
                                await call.message.answer("Печально")
                                await bot.send_message(offer["seller"], "Покупатель отменил заказ")
                                db['active_deals'].delete_one({"_id":ObjectId(data_mas[0])})
                                db["users"].update_one({"telegram_id":call.message.chat.id}, {"$inc":{"balance":offer["cost"]}})
                                db['users'].update_one({"telegram_id":call.message.chat.id}, {"$pull":{"deals":ObjectId(data_mas[0])}})
                                db['users'].update_one({"telegram_id":offer["seller"]}, {"$pull":{"deals":ObjectId(data_mas[0])}})
                                db["l2m"].update_one({"_id":offer["offer_id"]}, {"$set":{"invis":False}})
                                await deals_process(call.message, state, db)
                            else:
                                await call.message.answer("Продавец принял заказ в работу, действуй согласно инструкциям ниже")

                        case "buyer_accept":
                            db["users"].update_one({"telegram_id":offer["seller"]}, {"$inc":{"balance":offer["cost"]}})
                            db["active_deals"].update_one({"_id":ObjectId(offer["_id"])}, {"$set":{"status":"well done"}})
                            db["l2m"].delete_one({"_id":offer["offer_id"]})
                            await bot.send_message(offer["seller"], "Покупатель подтвердил выполнение заказа, на ваш баланс зачисленно "+ str(offer["cost"]))
                            await call.message.answer("Поздравляем с приобретением!")
                            await deals_process(call.message, state, db)

                        case "report" | "decision":
                            await call.message.answer("Пока что не работает, функционал админ панели")
                            await one_active_deal(call, state, db)
                    
                case"cat_accounts":


                    match data_mas[2]:
                        
                        case "yes" | "no":
                           await accounts_seller_start(call, state, db, bot, True)
                            
                        case "buyer_no":
                            if offer["status"] == "seller await":
                                await call.message.answer("Печально")
                                await bot.send_message(offer["seller"], "Покупатель отменил заказ")
                                db['active_deals'].delete_one({"_id":ObjectId(data_mas[0])})
                                db["users"].update_one({"telegram_id":call.message.chat.id}, {"$inc":{"balance":offer["cost"]}})
                                db['users'].update_one({"telegram_id":call.message.chat.id}, {"$pull":{"deals":ObjectId(data_mas[0])}})
                                db['users'].update_one({"telegram_id":offer["seller"]}, {"$pull":{"deals":ObjectId(data_mas[0])}})
                                db["l2m"].update_one({"_id":offer["offer_id"]}, {"$set":{"invis":False}})
                                await deals_process(call.message, state, db)
                            else:
                                await call.message.answer("Продавец принял заказ в работу, действуй согласно инструкциям ниже")

                        case "buyer_accept":
                            db["users"].update_one({"telegram_id":offer["seller"]}, {"$inc":{"balance":offer["cost"]}})
                            db["active_deals"].update_one({"_id":ObjectId(offer["_id"])}, {"$set":{"status":"well done"}})
                            db["l2m"].delete_one({"_id":offer["offer_id"]})
                            await bot.send_message(offer["seller"], "Покупатель подтвердил выполнение заказа, на ваш баланс зачисленно "+ str(offer["cost"]))
                            await call.message.answer("Поздравляем с приобретением!")
                            await deals_process(call.message, state, db)

                        case "report" | "decision":
                            await call.message.answer("Пока что не работает, функционал админ панели")
                            await one_active_deal(call, state, db)

                case"cat_things":


                    match data_mas[2]:
                        
                        case "yes" | "no":
                           await things_seller_start(call, state, db, bot, True)
                            
                        case "buyer_no":
                            if offer["status"] == "seller await":
                                await call.message.answer("Печально")
                                await bot.send_message(offer["seller"], "Покупатель отменил заказ")
                                db['active_deals'].delete_one({"_id":ObjectId(data_mas[0])})
                                db["users"].update_one({"telegram_id":call.message.chat.id}, {"$inc":{"balance":offer["cost"]}})
                                db['users'].update_one({"telegram_id":call.message.chat.id}, {"$pull":{"deals":ObjectId(data_mas[0])}})
                                db['users'].update_one({"telegram_id":offer["seller"]}, {"$pull":{"deals":ObjectId(data_mas[0])}})
                                db["l2m"].update_one({"_id":offer["offer_id"]}, {"$set":{"invis":False}})
                                await deals_process(call.message, state, db)
                            else:
                                await call.message.answer("Продавец принял заказ в работу, действуй согласно инструкциям ниже")


                        case "buyer_accept":
                            db["users"].update_one({"telegram_id":offer["seller"]}, {"$inc":{"balance":offer["cost"]}})
                            db["active_deals"].update_one({"_id":ObjectId(offer["_id"])}, {"$set":{"status":"well done"}})
                            db["l2m"].delete_one({"_id":offer["offer_id"]})
                            await bot.send_message(offer["seller"], "Покупатель подтвердил выполнение заказа, на ваш баланс зачисленно "+ str(offer["cost"]))
                            await call.message.answer("Поздравляем с приобретением!")
                            await deals_process(call.message, state, db)

                        case "report" | "decision":
                            await call.message.answer("Пока что не работает, функционал админ панели")
                            await one_active_deal(call, state, db)


                    

    



   







