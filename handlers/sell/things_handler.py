from aiogram import Dispatcher
from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from exchange_f.sell_f.things import *
from exchange_f.exchange import server_process
from functools import partial

async def things_description_handler(call:types.CallbackQuery, state:FSMContext):
    await call.message.delete()
    await thing_description(call, state)

async def things_cost_handler(message:types.Message, state:FSMContext):
    await thing_cost(message, state)

async def things_check_handler(message:types.Message, state:FSMContext):
    await thing_check(message, state)

async def things_set_handler(call:types.CallbackQuery, state:FSMContext, db:Database):
    await call.message.delete()
    match call.data.replace("sell_", ""):
        case "post":
            await thing_db_set(call, state, db)
        case "redact":
            await server_process(call, state, True)

def things_sell_handlers(dp: Dispatcher, dbc:Database):
    new_things_set_handler = partial(things_set_handler, db=dbc)
    dp.register_callback_query_handler(things_description_handler, lambda c:c.data.startswith("things_"), state = things_states.thing_type)
    dp.register_message_handler(things_cost_handler, state=things_states.description)
    dp.register_message_handler(things_check_handler, state = things_states.cost)
    dp.register_callback_query_handler(new_things_set_handler, lambda c: c.data.startswith("sell_"), state=things_states.cost)

   




