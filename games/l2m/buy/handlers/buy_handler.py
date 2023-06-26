from aiogram.dispatcher import FSMContext
from aiogram import types
from pymongo.database import Database
from aiogram import Dispatcher
from functools import partial

from ..buy import *


from chat.chat import chat_start


async def buyer_accept_handler(call:types.CallbackQuery, state:FSMContext, db:Database, bot:Bot):
    await call.message.delete()
    await buyer_accept(call, state, db, bot)


async def balance_add_process_handler(call:types.CallbackQuery, state:FSMContext, db:Database):
    await call.message.delete()
    await balance_add_process(call, state, db)

async def buy_cancel_handler(call:types.CallbackQuery, state:FSMContext, db:Database):
    await call.message.delete()
    await buy_cancel(call, state, db)


async def chat_start_handler(call:types.CallbackQuery, state:FSMContext, db:Database,dp:Dispatcher, bot:Bot):
    await chat_start(call, state, db,dp, bot)


def buy_handlers(dpc:Dispatcher, dbc:Database, botc:Bot):

    new_buyer_accept_handler = partial(buyer_accept_handler, db=dbc, bot=botc)
    dpc.register_callback_query_handler(new_buyer_accept_handler, lambda c: c.data.startswith("buyer_accept:"), state="*")


    new_chat_start_handler = partial(chat_start_handler, db=dbc, bot=botc, dp=dpc)
    dpc.register_callback_query_handler(new_chat_start_handler, lambda c: c.data.startswith("buyer_chat:"), state="*")

    new_balance_add_process_handler = partial(balance_add_process_handler, db=dbc)
    new_buy_cancel_handler = partial(buy_cancel_handler, db=dbc)

    dpc.register_callback_query_handler(new_balance_add_process_handler, lambda c: c.data == "no_balance_add", state="*")
    dpc.register_callback_query_handler(new_buy_cancel_handler, lambda c:c.data == "no_balance_cancel", state="*")