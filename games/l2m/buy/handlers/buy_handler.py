from aiogram.dispatcher import FSMContext
from aiogram import types
from pymongo.database import Database
from aiogram import Dispatcher
from functools import partial

from ..buy import *


async def balance_add_process_handler(call:types.CallbackQuery, state:FSMContext, db:Database):
    await call.message.delete()
    await balance_add_process(call, state, db)

async def buy_cancel_handler(call:types.CallbackQuery, state:FSMContext, db:Database):
    await call.message.delete()
    await buy_cancel(call, state, db)


def buy_handlers(dp:Dispatcher, dbc:Database):
    new_balance_add_process_handler = partial(balance_add_process_handler, db=dbc)
    new_buy_cancel_handler = partial(buy_cancel_handler, db=dbc)

    dp.register_callback_query_handler(new_balance_add_process_handler, lambda c: c.data == "no_balance_add", state=buy_list.buy_start)
    dp.register_callback_query_handler(new_buy_cancel_handler, lambda c:c.data == "no_balance_cancel", state=buy_list.buy_start)
