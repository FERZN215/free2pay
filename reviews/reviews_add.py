
from aiogram.dispatcher import FSMContext
from aiogram import types
from pymongo.database import Database
from aiogram.dispatcher.filters.state import State, StatesGroup

from keyboards.review_add_kb import add_reviews_kb

from datetime import datetime

class reviews_add_states(StatesGroup):
    review = State()
    num = State()

async def reviews_add(call:types.CallbackQuery, state:FSMContext):
    data = await state.get_data()
    if data.get("prev_state"):
        await reviews_add_states.review.set()
    else:
        if await state.get_state() == "active_deals_list:id":
            await reviews_add_states.review.set()
        else:
            await state.update_data(prev_state = await state.get_state())
            await reviews_add_states.review.set()



    await call.message.answer("Оставьте отзыв одним сообщением", reply_markup = add_reviews_kb)


async def text_process(message:types.Message, state:FSMContext):
    await reviews_add_states.num.set()
    await state.update_data(new_review_txt = message.text)
    await message.answer("Введи оценку от 1 до 5:")

async def num_process(message:types.Message, state:FSMContext, db:Database):
    data = await state.get_data()
    if not message.text.isdigit():
        await message.answer("Оценка должна быть целым числом")
        return

    if int(message.text) > 5 or int(message.text) < 1:
        await message.answer("Оценка должна быть целым числом от 1 до 5")
        return

    cur_time = datetime.now()
    user = db["users"].find_one({"telegram_id":message.chat.id})
    db["users"].update_one({"telegram_id":data.get("seller_id_r")}, {"$push":{"reviews":{
        "name":user["local_name"],
        "rating":int(message.text),
        "description":data.get("new_review_txt"),
        "date":str(str(cur_time.day) +"."+str(cur_time.month))
    }}})

    await message.answer("Спасибо за отзыв")
    if data.get("prev_state"):
        await state.set_state(data.get("prev_state"))
    else:
        await state.finish()
    
    



    








async def reviews_add_cancel(call:types.CallbackQuery, state:FSMContext):
    await call.message.delete()

    if await state.get_state() == "reviews_add_states:review":
        
        data = await state.get_data()
        if data.get("prev_state"):
            await state.set_state(data.get("prev_state"))
        else:
            await state.finish()
        await call.message.answer("Sad(")
