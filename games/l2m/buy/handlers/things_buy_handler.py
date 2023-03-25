from aiogram.dispatcher import FSMContext
from aiogram import types, Bot
from pymongo.database import Database
from aiogram import Dispatcher
from functools import partial

from chat.chat import chat_start

from ..things import *
from ..buy import things_buy_process
from reviews.reviews import view_reviews

async def things_kb_handler(call:types.CallbackQuery, state:FSMContext, db:Database):
    await things_kb_pr(call, state, db)

async def things_by_one_handler(call:types.CallbackQuery, state:FSMContext, db:Database):
    await call.message.delete()
    await one_thing_offer(call, state, db)

async def buy_porcess_start_handler(call:types.CallbackQuery, state:FSMContext, db:Database, bot:Bot):
    await call.message.delete()
    await things_buy_process(call, state, db, bot)


async def back_buttons_handler(call:types.CallbackQuery, state:FSMContext, db:Database):
    await call.message.delete()
    await state.update_data(id = None)
    await things_out(call, state, db)

async def chat_start_handler(call:types.CallbackQuery, state:FSMContext, db:Database, bot:Bot):
    await chat_start(call, state, db, bot )


def things_buy_handler(dp:Dispatcher, dbc:Database, botc:Bot):
    new_things_kb_handler = partial(things_kb_handler, db=dbc)
    new_things_by_one_handler = partial(things_by_one_handler, db=dbc)
    new_back_buttons_handler = partial(back_buttons_handler, db=dbc)
    new_buy_porcess_start_handler = partial(buy_porcess_start_handler, db = dbc, bot=botc)
    new_chat_start_handler = partial(chat_start_handler, db=dbc, bot=botc)


    new_view_reviews = partial(view_reviews, db=dbc)
    dp.register_callback_query_handler(new_view_reviews, lambda c:c.data=="buyer_reviews", state=things_list.id)

    dp.register_callback_query_handler(new_things_kb_handler, lambda c: c.data.endswith("_offers"), state=things_list.cur_list)
    dp.register_callback_query_handler(new_things_by_one_handler, lambda c: c.data.startswith("th_offer_id:"), state=things_list.cur_list)
    dp.register_callback_query_handler(new_buy_porcess_start_handler, lambda c: c.data == "buyer_buy", state=things_list.id)

    dp.register_callback_query_handler(new_chat_start_handler, lambda c: c.data == "buyer_chat", state=things_list.id)


    dp.register_callback_query_handler(new_back_buttons_handler, lambda c: c.data=="back_from_one", state=things_list.id)