
from aiogram.dispatcher import FSMContext
from aiogram import types
from pymongo.database import Database
from aiogram.dispatcher.filters.state import State, StatesGroup

from keyboards.menu import menu_kb

from reviews.review_keyboard import reviews_kb, back_kb
from start.personal_area import personal_area

class my_review_list(StatesGroup):
    my_review_list = State()

async def view_reviews(call:types.CallbackQuery, state:FSMContext, db:Database):
    
   
    user = db["users"].find_one({"telegram_id":call.message.chat.id})
    await my_review_list.my_review_list.set()
    await state.update_data(my_review_list = 10)
    if len(user["reviews"]) <= 0:
        await call.message.answer("У вас нет отзывов", reply_markup=menu_kb)
        return

    await call.message.answer("Вот все твои отзывы: ", reply_markup=reviews_kb(user["reviews"][:11], 10))   

async def review_kb_process(call:types.CallbackQuery, state:FSMContext, db:Database):
    data = await state.get_data()
    user = db["users"].find_one({"telegram_id": call.message.chat.id })
    match call.data.replace("_reviews", ""):
        case "forward":
            _cur_list = data.get("my_review_list") + 10

            _reviews = user["reviews"][data.get("my_review_list"): _cur_list+1]
            
        case "back":
            _cur_list = data.get("my_review_list") - 10

            _reviews = user["reviews"][_cur_list-10:_cur_list+1]
        case "cancel":
            await call.message.delete()
            await state.finish()
            await personal_area(call.message, db)
            return
    await state.update_data(my_review_list = _cur_list)

    await call.message.edit_reply_markup(reviews_kb(_reviews, _cur_list))





async def view_one_review(call:types.CallbackQuery, state:FSMContext, db:Database):
    
    user = db["users"].find_one({"telegram_id": call.message.chat.id})

    await call.message.answer("Автор: "+ str(user["reviews"][int(call.data.replace("review_id:", ""))]["name"]) + 
                              "\nОценка: " + str(user["reviews"][int(call.data.replace("review_id:", ""))]["rating"]) + 
                              "\nТекст: "+ str(user["reviews"][int(call.data.replace("review_id:", ""))]["description"]), reply_markup=back_kb)
