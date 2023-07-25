from aiogram.dispatcher import FSMContext
from aiogram import types, Bot
from pymongo.database import Database
from aiogram import Dispatcher
from functools import partial
from chat.chat import chat_start

from ..accounts import *


from reviews.reviews import view_reviews


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



async def accounts_kb_handler(call:types.CallbackQuery, state:FSMContext, db:Database):
    await account_kb_pr(call, state, db)

async def account_by_one_handler(call:types.CallbackQuery, state:FSMContext, db:Database):
    await call.message.delete()
    await one_account_offer(call, state, db)


async def buy_porcess_start_handler(call:types.CallbackQuery, state:FSMContext, db:Database, bot:Bot):
    await call.message.delete()
    await accounts_buy_process(call, state, db, bot)


async def back_buttons_handler(call:types.CallbackQuery, state:FSMContext, db:Database):
    await call.message.delete()
    await state.update_data(id = None)
    await accounts_out(call, state, db)


async def chat_start_handler(call:types.CallbackQuery, state:FSMContext, db:Database, dp:Dispatcher, bot:Bot):
    await chat_start(call, state, db,dp, bot )

async def delete_accounts_offer_handler(call:types.CallbackQuery, state:FSMContext, db:Database):
    await call.message.delete()
    await delete_accounts_offer(call, state, db)

def accounts_buy_handler(dp:Dispatcher, dbc:Database, botc:Bot):
    new_accounts_kb_handler = partial(accounts_kb_handler, db=dbc)
    new_account_by_one_handler = partial(account_by_one_handler, db=dbc)
    new_back_buttons_handler = partial(back_buttons_handler, db=dbc)
    new_buy_porcess_start_handler = partial(buy_porcess_start_handler, db = dbc, bot=botc)
    new_chat_start_handler = partial(chat_start_handler, db=dbc, bot=botc, dp=dp)
    new_delete_diamond_offer_handler = partial(delete_accounts_offer_handler, db=dbc)

    new_account_seller_start_handler = partial(account_seller_start_handler, db=dbc, bot=botc )
    new_account_get_login_handler = partial(account_get_login_handler)
    new_account_get_password_handler = partial(account_get_password_handler, db=dbc, bot=botc )

    new_account_get_code_awaiting_handler = partial(account_get_code_awaiting_handler, db=dbc, bot=botc, dp = dp)
    new_account_send_code_handler = partial(account_send_code_handler, db=dbc, bot=botc, dp= dp )

    

    dp.register_callback_query_handler(new_account_seller_start_handler, lambda c: "_buy_accounts_start_" in c.data, state="*")
    dp.register_message_handler(new_account_get_login_handler, state=buy_list.login_input)
    dp.register_message_handler(new_account_get_password_handler, state=buy_list.password_input)

    dp.register_callback_query_handler(new_account_get_code_awaiting_handler, lambda c: c.data.startswith("buyer_code_query:"), state="*")
    dp.register_message_handler(new_account_send_code_handler, state=buy_list.verification_code)

    new_view_reviews = partial(view_reviews, db=dbc)
    dp.register_callback_query_handler(new_view_reviews, lambda c:c.data=="buyer_reviews", state=accounts_list.id)

    
    dp.register_callback_query_handler(new_accounts_kb_handler, lambda c: c.data.endswith("_offers") or c.data.startswith("account_"), state=accounts_list.cur_list)
    dp.register_callback_query_handler(new_account_by_one_handler, lambda c: c.data.startswith("acc_offer_id:"), state=accounts_list.cur_list)

    dp.register_callback_query_handler(new_buy_porcess_start_handler, lambda c: c.data == "buyer_buy", state=accounts_list.id)

    dp.register_callback_query_handler(new_chat_start_handler, lambda c: c.data == "buyer_chat", state=accounts_list.id)
    dp.register_callback_query_handler(new_delete_diamond_offer_handler, lambda c:c.data=="seller_delete", state=accounts_list.id)
    dp.register_callback_query_handler(new_back_buttons_handler, lambda c: c.data=="back_from_one", state=accounts_list.id)
