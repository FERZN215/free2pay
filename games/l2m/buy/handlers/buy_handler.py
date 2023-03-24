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


async def account_seller_start_handler(call:types.CallbackQuery, state:FSMContext, db:Database, bot:Bot):
    await call.message.delete()
    await accounts_seller_start(call, state, db, bot)

async def account_get_login_handler(message:types.Message, state:FSMContext):
    await accounts_get_login(message, state)

async def account_get_password_handler(message:types.Message, state:FSMContext, db:Database, bot:Bot):
    await accounts_get_password(message, state, db, bot)





async def account_get_code_awaiting_handler(call:types.CallbackQuery, state:FSMContext, db:Database, bot:Bot, dp:Dispatcher):
    await call.message.delete()
    await accounts_verification_code_awaiting(call, state, dp, bot, db)

async def account_send_code_handler(message:types.Message, state:FSMContext, db:Database, bot:Bot, dp:Dispatcher):
    await accounts_verification_code_from_seller(message, state, dp, bot, db)








async def balance_add_process_handler(call:types.CallbackQuery, state:FSMContext, db:Database):
    await call.message.delete()
    await balance_add_process(call, state, db)

async def buy_cancel_handler(call:types.CallbackQuery, state:FSMContext, db:Database):
    await call.message.delete()
    await buy_cancel(call, state, db)


def buy_handlers(dpc:Dispatcher, dbc:Database, botc:Bot):
    new_diamond_seller_start_handler = partial(diamond_seller_start_handler, db=dbc, bot=botc )
    new_diamond_get_lots_handler = partial(diamond_get_lots_handler, db=dbc, bot=botc )

    new_account_seller_start_handler = partial(account_seller_start_handler, db=dbc, bot=botc )
    new_account_get_login_handler = partial(account_get_login_handler)
    new_account_get_password_handler = partial(account_get_password_handler, db=dbc, bot=botc )

    new_account_get_code_awaiting_handler = partial(account_get_code_awaiting_handler, db=dbc, bot=botc, dp = dpc)
    new_account_send_code_handler = partial(account_send_code_handler, db=dbc, bot=botc, dp= dpc )

    dpc.register_callback_query_handler(new_diamond_seller_start_handler, lambda c: "_buy_diamonds_start_" in c.data, state="*")
    dpc.register_message_handler(new_diamond_get_lots_handler, state=buy_list.seller_ready)
    

    dpc.register_callback_query_handler(new_account_seller_start_handler, lambda c: "_buy_accounts_start_" in c.data, state="*")
    dpc.register_message_handler(new_account_get_login_handler, state=buy_list.login_input)
    dpc.register_message_handler(new_account_get_password_handler, state=buy_list.password_input)

    dpc.register_callback_query_handler(new_account_get_code_awaiting_handler, lambda c: c.data.startswith("buyer_code_query:"), state="*")
    dpc.register_message_handler(new_account_send_code_handler, state=buy_list.verification_code)




    new_balance_add_process_handler = partial(balance_add_process_handler, db=dbc)
    new_buy_cancel_handler = partial(buy_cancel_handler, db=dbc)

    dpc.register_callback_query_handler(new_balance_add_process_handler, lambda c: c.data == "no_balance_add", state=buy_list.buy_start)
    dpc.register_callback_query_handler(new_buy_cancel_handler, lambda c:c.data == "no_balance_cancel", state=buy_list.buy_start)
