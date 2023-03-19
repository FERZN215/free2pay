from aiogram.dispatcher import FSMContext
from aiogram import types
from pymongo.database import Database
from aiogram import Dispatcher
from functools import partial


from ..services import *


async def services_kb_handler(call:types.CallbackQuery, state:FSMContext, db:Database):
    await services_kb_pr(call, state, db)

async def services_by_one_handler(call:types.CallbackQuery, state:FSMContext, db:Database):
    await call.message.delete()
    await one_service_offer(call, state, db)

async def back_buttons_handler(call:types.CallbackQuery, state:FSMContext, db:Database):
    await call.message.delete()
    await state.update_data(id = None)
    await services_out(call, state, db)

def services_buy_handler(dp:Dispatcher, dbc:Database):
    new_accounts_kb_handler = partial(services_kb_handler, db=dbc)
    new_account_by_one_handler = partial(services_by_one_handler, db=dbc)
    new_back_buttons_handler = partial(back_buttons_handler, db=dbc)
    dp.register_callback_query_handler(new_accounts_kb_handler, lambda c: c.data.endswith("_offers"), state=services_list.cur_list)
    dp.register_callback_query_handler(new_account_by_one_handler, lambda c: c.data.startswith("ser_offer_id:"), state=services_list.cur_list)
    dp.register_callback_query_handler(new_back_buttons_handler, lambda c: c.data=="back_from_one", state=services_list.cur_list)