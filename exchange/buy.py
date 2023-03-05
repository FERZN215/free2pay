from aiogram.dispatcher import FSMContext
from aiogram import types
from pymongo.database import Database
from aiogram.dispatcher.filters.state import State, StatesGroup

from keyboards.offers import offers_kb

class buy_states(StatesGroup):
    cur_list = State()

async def buy_init_process(call:types.CallbackQuery, state:FSMContext, db:Database):
    data = await state.get_data()
    match data.get("game_type"):
        case "cat_diamonds":
            await diamonds_buy(call, state, db)
        case "cat_services":
            await services_buy(call, state)
        case "cat_accounts":
            await accounts_buy(call, state)

async def diamonds_buy(call:types.CallbackQuery, state:FSMContext, db:Database, n = 10):
    data = await state.get_data()
    offers = []
    for offer in db["diamonds"].find({"game":data.get("game")}).sort("cost_per_one"):
        offers.append(offer)
     
    await buy_states.cur_list.set()
    await state.update_data(cur_list = n)
    await call.message.answer("Вот все наши предложения:", reply_markup=offers_kb(offers, n))

async def services_buy():
    return

async def accounts_buy():
    return 