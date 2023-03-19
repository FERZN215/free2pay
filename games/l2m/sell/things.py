from aiogram.dispatcher import FSMContext
from aiogram import types
from pymongo.database import Database
from aiogram.dispatcher.filters.state import State, StatesGroup
from ..keyboards.l2m_things import l2m_things_cat
from keyboards.sell_conf import sell_conf_kb
from keyboards.menu import menu_kb
from usefull.is_digit import is_digit
from usefull.th_type_to_text import type_to_text

class things_states(StatesGroup):
    thing_type = State()
    description = State()
    cost = State()


        
async def thing_type(call:types.CallbackQuery, state:FSMContext):
    await things_states.thing_type.set()
    await call.message.answer("Пожалуйста выберите тип предмета",reply_markup=l2m_things_cat)

async def thing_description(call:types.CallbackQuery, state:FSMContext):
    await state.update_data(thing_type = call.data)
    await things_states.description.set()
    await call.message.answer("Пожалуйста кратко опишите предмет (200 символов)\nНазвание, цвет предмета, заточка:")

async def thing_cost(message:types.Message, state:FSMContext):
    if(len(message.text)>200):
        await message.reply("Этот текст слишком большой (" + str(len(message.text)) + "), попробуй ещё раз:")
        return
    await state.update_data(description = message.text)
    await things_states.cost.set()
    await message.answer("Укажите цену:")

async def thing_check(message:types.Message, state:FSMContext):
    if not is_digit(message.text):
        await message.answer("Цена должна быть числом, повтори попытку:")
        return
    
    await state.update_data(cost = float(message.text.replace(',', '.')))
    data = await state.get_data()
    await message.answer(
        "Тип предмета: " + str(type_to_text(data.get("thing_type"))) + "\n" +
        "Описание: " + str(data.get("description")) + "\n" +
        "Цена: " + str(data.get("cost")), reply_markup=sell_conf_kb
    )
    
async def thing_db_set(call:types.CallbackQuery, state:FSMContext, db:Database):
    data = await state.get_data()
    db["l2m"].insert_one({
        "seller":call.message.chat.id,
        "game": data.get("game"), 
        "pr_type":data.get("game_type"),
        "server": data.get("server"), 
        "under_server": data.get("under_server"),
        "type": data.get("thing_type"),
        "description": data.get("description"),
        "cost":data.get("cost")
    })
    await state.finish()
    await call.message.answer("Твое предложение видно всем!", reply_markup=menu_kb)
