from aiogram.dispatcher import FSMContext
from aiogram import types
from pymongo.database import Database
from aiogram.dispatcher.filters.state import State, StatesGroup

from usefull.is_digit import is_digit
from usefull.com_sw import com_sw

from keyboards.menu import menu_kb
from keyboards.l2m_servers import l2m_servers
from keyboards.l2m_under_servers import l2m_under_servers
from keyboards.comission import comission_kb
from keyboards.sell_conf import sell_conf_kb

class sell_states(StatesGroup):
    diamonds = State()
    diamonds_cost = State()
    comission = State()
    server = State()
    under_server = State()




async def sell_init_process(call:types.CallbackQuery, state:FSMContext):
    data = await state.get_data()
    match data.get("game_type"):
        case "cat_diamonds":
            await diamonds_server(call, state)
        case "cat_services":
            await services_sell(call, state)
        case "cat_accounts":
            await accounts_sell(call, state)


async def diamonds_server(call:types.CallbackQuery, state:FSMContext):
    await sell_states.server.set()
    await call.message.answer("Выбери сервер для продажи:", reply_markup=l2m_servers)


async def diamonds_under_server(call:types.CallbackQuery, state:FSMContext):
    await state.update_data(server = call.data)
    await sell_states.under_server.set()
    await call.message.answer("Выбери название сервера",reply_markup=l2m_under_servers)


async def diamonds_count(call:types.CallbackQuery, state:FSMContext):
    await state.update_data(under_server = call.data)
    await sell_states.diamonds.set()
    await call.message.answer("Сколько алмазов ты хочешь продать?")


async def diamonds_cost(message:types.Message, state:FSMContext):
    if message.text.isdigit() == False:
        await message.answer("Количество алмазов нужно ввести числом. Попробуй еще раз:")
        return
    await state.update_data(diamonds = int(message.text))
    await sell_states.diamonds_cost.set()
    await message.answer("Запомнил. Теперь напиши цену за один алмаз:")

async def commission(message:types.Message, state:FSMContext):
    if is_digit(message.text) == False:
        await message.answer("Цену одного алмаза нужно ввести числом. Попробуй еще раз:")
        return
    await state.update_data(diamonds_cost=float(message.text))
    await sell_states.comission.set()
    await message.answer("оплачивает ли вы внутриигровую  комиссию?", reply_markup=comission_kb)


async def diamonds_set(call:types.CallbackQuery, state:FSMContext, db:Database):
    await state.update_data(comission=call.data)
    data = await state.get_data()
    cur_seller = db["users"].find_one({"telegram_id":call.message.chat.id})
    await call.message.answer("Продавец: " + str(cur_seller["local_name"]) + "\nКоличество алмазов: " +str(data.get("diamonds")) + "\nЦена за единицу: " +str(data.get("diamonds_cost")) +"\nКоммиссия:" + str(com_sw(data.get("comission"))) + "\nРейтинг: 96%", reply_markup=sell_conf_kb)

async def redact_diamonds(call:types.CallbackQuery ,state:FSMContext):
    await diamonds_server(call, state)


async def diamonds_db_set(call:types.CallbackQuery, state:FSMContext,  db:Database ):
    data = await state.get_data()

    db["diamonds"].insert_one(
    {"game": data.get("game"), "server": data.get("server"), "under_server": data.get("under_server"),
    "seller": call.message.chat.id, "count": data.get("diamonds"),"comission": data.get("comission"), "cost_per_one": data.get("diamonds_cost")})
    await state.finish()
    await call.message.answer("Твое предложения видно всем!", reply_markup=menu_kb)



async def services_sell(call:types.CallbackQuery, state:FSMContext):
    return


async def accounts_sell(call:types.CallbackQuery, state:FSMContext):
    return

