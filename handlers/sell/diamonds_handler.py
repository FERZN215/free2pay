from aiogram import Dispatcher
from aiogram import types
from aiogram.dispatcher import FSMContext
from exchange_f.sell_f.wallet.diamonds import *
from exchange_f.exchange import server_process
from functools import partial


async def diamonds_handler(message:types.Message, state:FSMContext):
    await diamonds_cost(message, state)

async def commission_handler(message:types.Message, state:FSMContext):
    await commission(message, state)

async def diamonds_cost_handler(call:types.CallbackQuery, state:FSMContext):
    await call.message.delete()
    await diamonds_set(call, state)

async def diamonds_final_process(call:types.CallbackQuery, state:FSMContext, db:Database):
    await call.message.delete()
    match call.data.replace("sell_", ""):
        case "post":
            await diamonds_db_set(call, state, db)
        case "redact":
            await server_process(call, state, True)


def diamonds_sell_handlers(dp: Dispatcher, dbc:Database):
   
    new_diamonds_final_process = partial(diamonds_final_process, db=dbc)
    dp.register_message_handler(diamonds_handler, state=diamods_states.diamonds)
    dp.register_message_handler(commission_handler, state=diamods_states.diamonds_cost)
    dp.register_callback_query_handler(diamonds_cost_handler, lambda c: c.data.startswith("comission_"), state=diamods_states.comission)
    dp.register_callback_query_handler(new_diamonds_final_process, lambda c: c.data.startswith("sell_"), state=diamods_states.comission)

