
from aiogram.dispatcher import FSMContext
from aiogram import types
from pymongo.database import Database
from aiogram.dispatcher.filters.state import State, StatesGroup

from games.l2m.buy.accounts import one_account_offer
from games.l2m.buy.things import one_thing_offer
from games.l2m.buy.services import one_service_offer
from games.l2m.buy.diamonds import one_diamond_offer
from usefull.converters import chat_db_conver

from .review_keyboard import reviews_kb, back_kb

class review_list(StatesGroup):
    review_list = State()

async def view_reviews(call:types.CallbackQuery, state:FSMContext, db:Database):
    await call.message.delete()
    data = await state.get_data()
    user = db["users"].find_one({"telegram_id": (db[chat_db_conver(data.get("game"))].find_one({"_id": data.get("id")}))["seller"]})
    await review_list.review_list.set()
    await state.update_data(review_list = 10)
    if len(user["reviews"]) <= 0:
        await call.message.answer("У данного продавца отсутствуют отзывы, повод задуматься")
        match data.get("game_type"):
            case "cat_accounts":
                await one_account_offer(call, state, db, True)
            case "cat_diamonds":
                await one_diamond_offer(state=state, db=db, msg=call.message)
            case "cat_things":
                await one_thing_offer(call, state, db, True)
            case "cat_services":
                await one_service_offer(call, state, db, True)
            
        return

    await call.message.answer("Вот все отзывы данного продавца: ", reply_markup=reviews_kb(user["reviews"][:11], 10))   

async def review_kb_process(call:types.CallbackQuery, state:FSMContext, db:Database):
    data = await state.get_data()
    user = db["users"].find_one({"telegram_id": (db[chat_db_conver(data.get("game"))].find_one({"_id": data.get("id")}))["seller"]})
    match call.data.replace("_reviews", ""):
        case "forward":
            _cur_list = data.get("review_list") + 10

            _reviews = user["reviews"][data.get("review_list"): _cur_list+1]
            
        case "back":
            _cur_list = data.get("review_list") - 10

            _reviews = user["reviews"][_cur_list-10:_cur_list+1]
        case "cancel":
            await call.message.delete()
            match data.get("game_type"):
                case "cat_accounts":
                    await one_account_offer(call, state, db, True)
                case "cat_diamonds":
                    await one_diamond_offer(state=state, db=db, msg=call.message)
                case "cat_things":
                    await one_thing_offer(call, state, db, True)
                case "cat_services":
                    await one_service_offer(call, state, db, True)
            # await one_account_offer(call, state, db, True)
            return
    await state.update_data(review_list = _cur_list)
    await call.message.edit_reply_markup(reviews_kb(_reviews, _cur_list))





async def view_one_review(call:types.CallbackQuery, state:FSMContext, db:Database):
    data = await state.get_data()
    user = db["users"].find_one({"telegram_id": (db[chat_db_conver(data.get("game"))].find_one({"_id": data.get("id")}))["seller"]})
    await call.message.answer("Автор: "+ str(user["reviews"][int(call.data.replace("review_id:", ""))]["name"]) + 
                              "\nОценка: " + str(user["reviews"][int(call.data.replace("review_id:", ""))]["rating"]) + 
                              "\nТекст: "+ str(user["reviews"][int(call.data.replace("review_id:", ""))]["description"]), reply_markup=back_kb)
