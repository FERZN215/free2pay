from aiogram.dispatcher import FSMContext
from aiogram import types
from pymongo.database import Database
from aiogram import Dispatcher
from functools import partial

from ..buy import *






async def diamond_seller_start_handler(call:types.CallbackQuery, state:FSMContext, db:Database, bot:Bot):
    await call.message.delete()
    await diamond_seller_start(call, state, db, bot)

async def diamond_get_lots_handler(message:types.Message, state:FSMContext, db:Database, bot:Bot):
    await diamond_get_lots(message, state, db, bot)











async def balance_add_process_handler(call:types.CallbackQuery, state:FSMContext, db:Database):
    await call.message.delete()
    await balance_add_process(call, state, db)

async def buy_cancel_handler(call:types.CallbackQuery, state:FSMContext, db:Database):
    await call.message.delete()
    await buy_cancel(call, state, db)


def buy_handlers(dp:Dispatcher, dbc:Database, botc:Bot):
    new_diamond_seller_start_handler = partial(diamond_seller_start_handler, db=dbc, bot=botc )
    new_diamond_get_lots_handler = partial(diamond_get_lots_handler, db=dbc, bot=botc )

    dp.register_callback_query_handler(new_diamond_seller_start_handler, lambda c: "_buy_start_" in c.data, state="*")
    dp.register_message_handler(new_diamond_get_lots_handler, state=buy_list.seller_ready)
    




    new_balance_add_process_handler = partial(balance_add_process_handler, db=dbc)
    new_buy_cancel_handler = partial(buy_cancel_handler, db=dbc)

    dp.register_callback_query_handler(new_balance_add_process_handler, lambda c: c.data == "no_balance_add", state=buy_list.buy_start)
    dp.register_callback_query_handler(new_buy_cancel_handler, lambda c:c.data == "no_balance_cancel", state=buy_list.buy_start)
