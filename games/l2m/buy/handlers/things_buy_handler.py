from aiogram.dispatcher import FSMContext
from aiogram import types, Bot
from pymongo.database import Database
from aiogram import Dispatcher
from functools import partial

from chat.chat import chat_start

from ..things import *
from ..buy import things_buy_process
from reviews.reviews import view_reviews



#----------------------------------------------------

async def things_seller_start_handler(call:types.CallbackQuery, state:FSMContext, db:Database, bot:Bot):
    await call.message.delete()
    await things_seller_start(call, state, db, bot)


async def thing_sell_type_process_handler(call:types.CallbackQuery, state:FSMContext, db:Database, bot:Bot):
    await call.message.delete()
    await thing_sell_type_process(call, state, db, bot)


async def buyer_trade_thing_handler(call:types.CallbackQuery, state:FSMContext, db:Database, bot:Bot, dp:Dispatcher):
    await call.message.delete()
    await bueyr_trade_thing(call, state, db, bot, dp)

async def au_cost_handler(message:types.Message, state:FSMContext, db:Database, bot:Bot):
    await au_cost(message, state, db, bot)

async def trade_desc_handler(message:types.Message, state:FSMContext, db:Database, bot:Bot):
    await trade_desc(message, state, db, bot)

#----------------------------------------------------
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

async def chat_start_handler(call:types.CallbackQuery, state:FSMContext, db:Database,dp:Dispatcher, bot:Bot):
    await chat_start(call, state, db, dp,bot )

async def delete_things_offer_handler(call:types.CallbackQuery, state:FSMContext, db:Database):
    await call.message.delete()
    await delete_things_offer(call, state, db)

def things_buy_handler(dp:Dispatcher, dbc:Database, botc:Bot):
    new_things_kb_handler = partial(things_kb_handler, db=dbc)
    new_things_by_one_handler = partial(things_by_one_handler, db=dbc)
    new_back_buttons_handler = partial(back_buttons_handler, db=dbc)
    new_buy_porcess_start_handler = partial(buy_porcess_start_handler, db = dbc, bot=botc)
    new_chat_start_handler = partial(chat_start_handler, db=dbc, bot=botc, dp=dp)
    new_delete_diamond_offer_handler = partial(delete_things_offer_handler, db=dbc)
    
    new_things_seller_start_handler = partial(things_seller_start_handler, db = dbc, bot=botc )
    new_thing_sell_type_process_handler = partial(thing_sell_type_process_handler,  db = dbc, bot=botc)
    new_bueyr_trade_thing_handler = partial(buyer_trade_thing_handler, db=dbc, bot=botc, dp=dp)
    new_au_cost_handler = partial(au_cost_handler,  db = dbc, bot=botc)
    new_trade_desc_handler = partial(trade_desc_handler, db=dbc, bot=botc)

    dp.register_callback_query_handler(new_things_seller_start_handler, lambda c:  "_buy_things_start_" in c.data, state="*")
    dp.register_callback_query_handler(new_thing_sell_type_process_handler, lambda c: c.data.startswith("thing_sell_"), state=buy_list.thing_sell_type)
    dp.register_callback_query_handler(new_bueyr_trade_thing_handler, lambda c: "_buyer_au_" in c.data, state="*")
    dp.register_message_handler(new_au_cost_handler, state=buy_list.au_cost)
    dp.register_message_handler(new_trade_desc_handler, state=buy_list.trade_desc)


    new_view_reviews = partial(view_reviews, db=dbc)
    dp.register_callback_query_handler(new_view_reviews, lambda c:c.data=="buyer_reviews", state=things_list.id)

    dp.register_callback_query_handler(new_things_kb_handler, lambda c: c.data.endswith("_offers") or c.data.startswith("things_"), state=things_list.cur_list)
    dp.register_callback_query_handler(new_things_by_one_handler, lambda c: c.data.startswith("th_offer_id:"), state=things_list.cur_list)
    dp.register_callback_query_handler(new_buy_porcess_start_handler, lambda c: c.data == "buyer_buy", state=things_list.id)

    dp.register_callback_query_handler(new_chat_start_handler, lambda c: c.data == "buyer_chat", state=things_list.id)

    dp.register_callback_query_handler(new_delete_diamond_offer_handler, lambda c:c.data=="seller_delete", state=things_list.id)
    dp.register_callback_query_handler(new_back_buttons_handler, lambda c: c.data=="back_from_one", state=things_list.id)