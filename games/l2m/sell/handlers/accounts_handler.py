from aiogram import Dispatcher
from aiogram import types
from aiogram.dispatcher import FSMContext
from ..accounts import *
from exchange_f.exchange import server_process
from functools import partial


async def account_type_handler(call:types.CallbackQuery, state:FSMContext):
    await call.message.delete()
    await account_type(call, state)


async def account_level_handler(call:types.CallbackQuery, state:FSMContext):
    await call.message.delete()
    await account_level(call, state)

async def account_cost_handler(message:types.Message, state:FSMContext):
    await account_cost(message, state)

async def account_description_handler(message:types.Message, state:FSMContext):
    await account_description(message, state)

async def accounts_screenshots_handler(message:types.Message, state:FSMContext):
    await accounts_screenshots(message, state)

async def accounts_check_handler(message:types.Message, state:FSMContext, db:Database):
    await accounts_check(message,state, db)

async def accounts_set_handler(call:types.CallbackQuery, state:FSMContext, db:Database):
    await call.message.delete()
    match call.data.replace("sell_", ""):
        case "post":
            await account_db_set(call, state, db)
        case "redact":
            await server_process(call, state, True)

def accounts_sell_handlers(dp: Dispatcher, dbc:Database):
    new_accounts_check_handler = partial(accounts_check_handler, db=dbc)
    new_accounts_set_handler = partial(accounts_set_handler, db=dbc)
    dp.register_callback_query_handler(account_level_handler, lambda c: c.data.startswith("account_"), state=accounts_states.acc_type)
    dp.register_message_handler(account_cost_handler, state = accounts_states.level)
    dp.register_message_handler(account_description_handler, state=accounts_states.cost)
    dp.register_message_handler(accounts_screenshots_handler, state=accounts_states.description)
    dp.register_message_handler(new_accounts_check_handler, state=accounts_states.photos)
    dp.register_callback_query_handler(new_accounts_set_handler,state=accounts_states.photos )