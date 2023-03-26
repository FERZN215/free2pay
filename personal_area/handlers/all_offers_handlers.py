from aiogram.dispatcher import FSMContext
from aiogram import types
from pymongo.database import Database
from aiogram import Dispatcher
from functools import partial

from start.personal_area import Profile

from ..all_offers import *



async def all_offers_kb_manager_handler(call:types.CallbackQuery, state:FSMContext, db:Database):
    await all_offers_kb_manager(call, state, db)


async def view_all_offers_handler(call:types.CallbackQuery, state:FSMContext, db:Database):
    await call.message.delete()
    await view_all_offers(call, state, db)

async def view_one_offer_handler(call:types.CallbackQuery, state:FSMContext, db:Database):
    await call.message.delete()
    await view_one_offer(call, state, db)

async def delete_all_offer_handler(call:types.CallbackQuery, state:FSMContext, db:Database):
    await call.message.delete()
    await delete_all_offer(call, state, db)

async def back_from_one_offer_handlers(call:types.CallbackQuery, state:FSMContext, db:Database):
    await call.message.delete()
    await back_from_one_offer(call,state, db)


async def change_diamond_count_handler(call:types.CallbackQuery, state:FSMContext, db:Database):
    await call.message.delete()
    await change_diamond_count(call, state, db)

async def change_diamond_count_process_handler(message:types.Message, state:FSMContext, db:Database):
    await change_diamond_count_process(message, state, db)

def all_offers_handlers(dp:Dispatcher, dbc:Database):
    new_all_offers_kb_manager = partial(all_offers_kb_manager, db=dbc)
    new_view_all_offers_handler = partial(view_all_offers_handler, db=dbc)
    new_view_one_offer_handler = partial(view_one_offer_handler, db=dbc)
    new_delete_all_offer_handler = partial(delete_all_offer_handler, db=dbc)
    new_back_from_one_offer_handlers = partial(back_from_one_offer_handlers, db=dbc)
    new_change_diamond_count_handler = partial(change_diamond_count_handler, db=dbc)
    new_change_diamond_count_process_handler = partial(change_diamond_count_process_handler, db=dbc)


    dp.register_callback_query_handler(new_change_diamond_count_handler, lambda c: c.data == "seller_count", state=all_offers_states.id)
    dp.register_message_handler(new_change_diamond_count_process_handler, state=all_offers_states.new_d_count)


    dp.register_callback_query_handler(new_all_offers_kb_manager, lambda c: c.data.endswith("_alloffers"), state=all_offers_states.offer_list)
    dp.register_callback_query_handler(new_view_all_offers_handler, lambda c:c.data == "all_offers", state=Profile.profile)
    dp.register_callback_query_handler(new_view_one_offer_handler, lambda c: c.data.startswith("all_offer_id:"), state=all_offers_states.offer_list)
    dp.register_callback_query_handler(new_delete_all_offer_handler, lambda c:c.data == "seller_delete", state=all_offers_states.id)
    dp.register_callback_query_handler(new_back_from_one_offer_handlers, lambda c:c.data=="back_from_one", state=all_offers_states.id)