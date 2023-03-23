from aiogram.dispatcher import FSMContext
from aiogram import types
from pymongo.database import Database
from aiogram.dispatcher.filters.state import State, StatesGroup

from keyboards.menu import menu_kb
from keyboards.comission import comission_kb
from keyboards.sell_conf import sell_conf_kb

from usefull.is_digit import is_digit
from usefull.com_sw import com_sw



class diamods_states(StatesGroup):
    diamonds = State()
    diamonds_cost = State()
    comission = State()






async def diamonds_count(call:types.CallbackQuery, state:FSMContext):
    await diamods_states.diamonds.set()
    await call.message.answer("Сколько алмазов ты хочешь продать?")


async def diamonds_cost(message:types.Message, state:FSMContext):
    if message.text.isdigit() == False:
        await message.answer("Количество алмазов нужно ввести числом. Попробуй еще раз:")
        return
    await state.update_data(diamonds = int(message.text))
    await diamods_states.diamonds_cost.set()
    await message.answer("Запомнил. Теперь напиши цену за один алмаз:")

async def commission(message:types.Message, state:FSMContext):
    if is_digit(message.text) == False:
        await message.answer("Цену одного алмаза нужно ввести числом. Попробуй еще раз:")
        return
    await state.update_data(diamonds_cost=float(message.text.replace(',', '.')))
    await diamods_states.comission.set()
    await message.answer("оплачивает ли вы внутриигровую  комиссию?", reply_markup=comission_kb)


async def diamonds_set(call:types.CallbackQuery, state:FSMContext):
    await state.update_data(comission=call.data)
    data = await state.get_data()
    
    await call.message.answer("Количество алмазов: " +str(data.get("diamonds")) + "\nЦена за единицу: " +str(data.get("diamonds_cost")) +"\nКоммиссия:" + str(com_sw(data.get("comission"))), reply_markup=sell_conf_kb)


async def diamonds_db_set(call:types.CallbackQuery, state:FSMContext,  db:Database ):
    data = await state.get_data()

    db["l2m"].insert_one(
    {"game": data.get("game"), "pr_type":data.get("game_type"), "server": data.get("server"), "under_server": data.get("under_server"),
    "seller": call.message.chat.id, "name": data.get("diamonds"),"comission": data.get("comission"), "cost": data.get("diamonds_cost")})
    await state.finish()
    await call.message.answer("Твое предложения видно всем!", reply_markup=menu_kb)