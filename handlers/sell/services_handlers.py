from aiogram import Dispatcher
from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from exchange_f.sell_f.services import *
from exchange_f.exchange import server_process
from functools import partial

async def services_name_handler(message:types.Message, state:FSMContext):
    await services_cost(message, state)

async def services_cost_handler(message:types.Message, state:FSMContext):
    await services_description(message, state)


async def services_description_handler(message:types.Message, state:FSMContext):
    await services_set(message, state)


async def services_set_handler(call:types.CallbackQuery, state:FSMContext, db:Database):
    await call.message.delete()
    match call.data.replace("sell_", ""):
        case "post":
            await services_db_set(call, state, db)
        case "redact":
            await server_process(call, state, True)

def services_sell_handlers(dp: Dispatcher, dbc:Database):
    
    new_services_set_handler = partial(services_set_handler, db=dbc)
    dp.register_message_handler(services_name_handler, state=services_states.name)
    dp.register_message_handler(services_cost_handler, state=services_states.cost)
    dp.register_message_handler(services_description_handler, state=services_states.description)
    dp.register_callback_query_handler(new_services_set_handler, lambda c: c.data.startswith("sell_"), state=services_states.description)



