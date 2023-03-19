from aiogram.dispatcher import FSMContext
from aiogram import types
from pymongo.database import Database
from aiogram import Dispatcher
from functools import partial

from ..diamonds import *


async def diamonds_kb_handler(call:types.CallbackQuery, state:FSMContext, db:Database):
    await diamonds_kb_pr(call, state, db)

async def diamonds_by_one_handler(call:types.CallbackQuery, state:FSMContext, db:Database):
    await call.message.delete()
    await one_diamond_offer(call, state, db)

async def back_buttons_handler(call:types.CallbackQuery, state:FSMContext, db:Database):
    await call.message.delete()
    await state.update_data(id = None)
    await diamonds_out(call, state, db)

def diamonds_buy_handlers(dp: Dispatcher, dbc:Database):
    new_diamonds_kb_handler = partial(diamonds_kb_handler, db=dbc)
    new_diamonds_buy_handlers = partial(diamonds_by_one_handler, db=dbc)
    new_back_buttons_handler = partial(back_buttons_handler, db=dbc)
    dp.register_callback_query_handler(new_diamonds_kb_handler, lambda c: c.data.endswith("_offers"), state=diamonds_list.cur_list )
    dp.register_callback_query_handler(new_diamonds_buy_handlers, lambda c: c.data.startswith("dia_offer_id:"), state=diamonds_list.cur_list )
    dp.register_callback_query_handler(new_back_buttons_handler, lambda c: c.data == "back_from_one",state=diamonds_list.cur_list )