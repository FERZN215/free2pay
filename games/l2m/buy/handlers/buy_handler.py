from aiogram.dispatcher import FSMContext
from aiogram import types
from pymongo.database import Database
from aiogram import Dispatcher
from functools import partial

from ..buy import *


from chat.chat import chat_start





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







async def things_seller_start_handler(call:types.CallbackQuery, state:FSMContext, db:Database, bot:Bot):
    await call.message.delete()
    await things_seller_start(call, state, db, bot)


async def thing_sell_type_process_handler(call:types.CallbackQuery, state:FSMContext, db:Database, bot:Bot):
    await call.message.delete()
    await thing_sell_type_process(call, state, db, bot)


async def bueyr_trade_thing_handler(call:types.CallbackQuery, state:FSMContext, db:Database, bot:Bot, dp:Dispatcher):
    await call.message.delete()
    await bueyr_trade_thing(call, state, db, bot, dp)

async def au_cost_handler(message:types.Message, state:FSMContext, db:Database, bot:Bot):
    await au_cost(message, state, db, bot)

async def trade_desc_handler(message:types.Message, state:FSMContext, db:Database, bot:Bot):
    await trade_desc(message, state, db, bot)



async def service_seller_start_handler(call:types.CallbackQuery, state:FSMContext, db:Database, bot:Bot):
    await call.message.delete()
    await services_seller_start(call, state, db, bot)

async def service_get_instructions_handler(message:types.Message, state:FSMContext,  db:Database, bot:Bot):
    await services_get_instruction(message, state, db, bot)




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


    new_buyer_accept_handler = partial(buyer_accept_handler, db=dbc, bot=botc)
    dpc.register_callback_query_handler(new_buyer_accept_handler, lambda c: c.data.startswith("buyer_accept:"), state="*")



    new_things_seller_start_handler = partial(things_seller_start_handler, db = dbc, bot=botc )
    new_thing_sell_type_process_handler = partial(thing_sell_type_process_handler,  db = dbc, bot=botc)
    new_bueyr_trade_thing_handler = partial(bueyr_trade_thing_handler, db=dbc, bot=botc, dp=dpc)
    new_au_cost_handler = partial(au_cost_handler,  db = dbc, bot=botc)
    new_trade_desc_handler = partial(trade_desc_handler, db=dbc, bot=botc)

    dpc.register_callback_query_handler(new_things_seller_start_handler, lambda c:  "_buy_things_start_" in c.data, state="*")
    dpc.register_callback_query_handler(new_thing_sell_type_process_handler, lambda c: c.data.startswith("thing_sell_"), state=buy_list.thing_sell_type)
    dpc.register_callback_query_handler(new_bueyr_trade_thing_handler, lambda c: "_buyer_au_" in c.data, state="*")
    dpc.register_message_handler(new_au_cost_handler, state=buy_list.au_cost)
    dpc.register_message_handler(new_trade_desc_handler, state=buy_list.trade_desc)

    
    new_service_seller_start_handler = partial(service_seller_start_handler, db=dbc, bot=botc)
    new_service_get_instructions_handler = partial(service_get_instructions_handler, db= dbc, bot=botc)

    dpc.register_callback_query_handler(new_service_seller_start_handler, lambda c: "_buy_services_start_" in c.data, state="*")
    dpc.register_message_handler(new_service_get_instructions_handler, state=buy_list.service_instruction)

    new_chat_start_handler = partial(chat_start_handler, db=dbc, bot=botc, dp=dpc)
    dpc.register_callback_query_handler(new_chat_start_handler, lambda c: c.data.startswith("buyer_chat:"), state="*")

    new_balance_add_process_handler = partial(balance_add_process_handler, db=dbc)
    new_buy_cancel_handler = partial(buy_cancel_handler, db=dbc)

    dpc.register_callback_query_handler(new_balance_add_process_handler, lambda c: c.data == "no_balance_add", state="*")
    dpc.register_callback_query_handler(new_buy_cancel_handler, lambda c:c.data == "no_balance_cancel", state="*")