from aiogram.dispatcher import FSMContext
from aiogram import types
from pymongo.database import Database
from aiogram import Dispatcher
from functools import partial


from ..accounts import *

from ..buy import accounts_buy_process
from reviews.reviews import view_reviews

async def accounts_kb_handler(call:types.CallbackQuery, state:FSMContext, db:Database):
    await account_kb_pr(call, state, db)

async def account_by_one_handler(call:types.CallbackQuery, state:FSMContext, db:Database):
    await call.message.delete()
    await one_account_offer(call, state, db)


async def buy_porcess_start_handler(call:types.CallbackQuery, state:FSMContext, db:Database):
    await call.message.delete()
    await accounts_buy_process(call, state, db)


async def back_buttons_handler(call:types.CallbackQuery, state:FSMContext, db:Database):
    await call.message.delete()
    await state.update_data(id = None)
    await accounts_out(call, state, db)



def accounts_buy_handler(dp:Dispatcher, dbc:Database):
    new_accounts_kb_handler = partial(accounts_kb_handler, db=dbc)
    new_account_by_one_handler = partial(account_by_one_handler, db=dbc)
    new_back_buttons_handler = partial(back_buttons_handler, db=dbc)
    new_buy_porcess_start_handler = partial(buy_porcess_start_handler, db = dbc)



    new_view_reviews = partial(view_reviews, db=dbc)
    dp.register_callback_query_handler(new_view_reviews, lambda c:c.data=="buyer_reviews", state=accounts_list.id)

    
    dp.register_callback_query_handler(new_accounts_kb_handler, lambda c: c.data.endswith("_offers"), state=accounts_list.cur_list)
    dp.register_callback_query_handler(new_account_by_one_handler, lambda c: c.data.startswith("acc_offer_id:"), state=accounts_list.cur_list)

    dp.register_callback_query_handler(new_buy_porcess_start_handler, lambda c: c.data == "buyer_buy", state=accounts_list.id)

    dp.register_callback_query_handler(new_back_buttons_handler, lambda c: c.data=="back_from_one", state=accounts_list.id)
