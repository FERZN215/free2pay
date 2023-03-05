from aiogram.dispatcher import FSMContext
from aiogram import types
from pymongo.database import Database
from aiogram.dispatcher.filters.state import State, StatesGroup
from keyboards.menu import menu_kb
from usefull.is_digit import is_digit

class sell_states(StatesGroup):
    diamonds = State()
    diamonds_cost = State()



async def sell_init_process(call:types.CallbackQuery, state:FSMContext):
    data = await state.get_data()
    match data.get("game_type"):
        case "cat_diamonds":
            await diamonds_sell(call, state)
        case "cat_services":
            await services_sell(call, state)
        case "cat_accounts":
            await accounts_sell(call, state)


async def diamonds_sell(call:types.CallbackQuery, state:FSMContext):
    await sell_states.diamonds.set()
    await call.message.answer("Сколько алмазов ты хочешь продать?")


async def diamonds_cost(message:types.Message, state:FSMContext):
    if message.text.isdigit() == False:
        await message.answer("Количество алмазов нужно ввести числом. Попробуй еще раз:")
        return
    await state.update_data(diamonds = int(message.text))
    await sell_states.diamonds_cost.set()
    await message.answer("Запомнил. Теперь напиши цену за один алмаз:")

async def diamonds_set(message:types.Message, state:FSMContext, db:Database):
    if is_digit(message.text) == False:
        await message.answer("Цену одного алмаза нужно ввести числом. Попробуй еще раз:")
        return
    await state.update_data(diamonds_cost=float(message.text))
    data = await state.get_data()
    db["diamonds"].insert_one({"game":data.get("game"),"seller":message.chat.id, "count":data.get("diamonds"), "cost_per_one":data.get("diamonds_cost")})
    await state.finish()
    await message.answer("Твое предложения видно всем!", reply_markup=menu_kb)




async def services_sell(call:types.CallbackQuery, state:FSMContext):
    return


async def accounts_sell(call:types.CallbackQuery, state:FSMContext):
    return

