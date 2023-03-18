from aiogram.dispatcher import FSMContext
from aiogram import types
from pymongo.database import Database
from aiogram.dispatcher.filters.state import State, StatesGroup
from keyboards.sell_conf import sell_conf_kb
from keyboards.menu import menu_kb

from usefull.is_digit import is_digit

class services_states(StatesGroup):
    name = State()
    cost = State()
    description = State()

async def services_name(call: types.CallbackQuery, state: FSMContext):
    await services_states.name.set()
    await call.message.answer("Напиши название услуги")


async def services_cost(message: types.Message, state: FSMContext):
    if len(message.text) > 45:
        await message.answer('Слишком большое название, попробуй еще раз:')
        return
    await state.update_data(name=message.text)
    await services_states.cost.set()
    await message.answer("Укажи цену услуги:")  


async def services_description(message: types.Message, state: FSMContext):
    if is_digit(message.text) == False:
        await message.answer("Цена должна быть числом, попробуй еще раз:")
        return
    await state.update_data(cost=float(message.text.replace(',', '.')))
    await services_states.description.set()
    await message.answer("Запомнил, теперь введи описание услуги")


async def services_set(message: types.Message, state: FSMContext):
    if len(message.text) > 200:
        await message.answer('Слишком большое описание, попробуй еще раз:')
        return
    await state.update_data(description=message.text)
    data = await state.get_data()
   
    await message.answer("Название: " +
        data.get("name") + "\nЦена " + str(data.get("cost")) + "\nОписание: "+str(data.get("description")), reply_markup=sell_conf_kb)



async def services_db_set(call: types.CallbackQuery, state: FSMContext, db: Database):
    data = await state.get_data()

    db["services"].insert_one(
        {"game": data.get("game"), "server": data.get("server"), "under_server": data.get("under_server"),
         "seller": call.message.chat.id, "name": data.get("name"), "cost": data.get("cost"), "description": data.get("description")})
    await state.finish()
    await call.message.answer("Твое предложения видно всем!", reply_markup=menu_kb)


