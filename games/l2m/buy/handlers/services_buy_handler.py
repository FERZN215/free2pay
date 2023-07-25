from aiogram.dispatcher import FSMContext
from aiogram import types
from pymongo.database import Database
from aiogram import Dispatcher, Bot
from functools import partial

from chat.chat import chat_start
from ..services import *

from reviews.reviews import view_reviews

async def services_kb_handler(call:types.CallbackQuery, state:FSMContext, db:Database):
    await services_kb_pr(call, state, db)

async def services_by_one_handler(call:types.CallbackQuery, state:FSMContext, db:Database):
    await call.message.delete()
    await one_service_offer(call, state, db)

async def back_buttons_handler(call:types.CallbackQuery, state:FSMContext, db:Database):
    await call.message.delete()
    await state.update_data(id = None)
    await services_out(call, state, db)

async def buy_porcess_start_handler(call:types.CallbackQuery, state:FSMContext, db:Database,  bot:Bot):
    await call.message.delete()
    await services_buy_process(call, state, db, bot)

async def chat_start_handler(call:types.CallbackQuery, state:FSMContext, db:Database, dp:Dispatcher,bot:Bot):
    await chat_start(call, state, db, dp,bot )

async def delete_services_offer_handler(call:types.CallbackQuery, state:FSMContext, db:Database):
    await call.message.delete()
    await delete_services_offer(call, state, db)

async def service_seller_start_handler(call:types.CallbackQuery, state:FSMContext, db:Database, bot:Bot):
    await call.message.delete()
    await services_seller_start(call, state, db, bot)

async def service_get_instructions_handler(message:types.Message, state:FSMContext,  db:Database, bot:Bot):
    await services_get_instruction(message, state, db, bot)



def services_buy_handler(dp:Dispatcher, dbc:Database, botc:Bot):
    new_accounts_kb_handler = partial(services_kb_handler, db=dbc)
    new_account_by_one_handler = partial(services_by_one_handler, db=dbc)
    new_back_buttons_handler = partial(back_buttons_handler, db=dbc)
    new_buy_porcess_start_handler = partial(buy_porcess_start_handler, db = dbc, bot=botc)
    new_chat_start_handler = partial(chat_start_handler, db=dbc, bot=botc, dp=dp)
    new_delete_diamond_offer_handler = partial(delete_services_offer_handler, db=dbc)
    new_service_seller_start_handler = partial(service_seller_start_handler, db=dbc, bot=botc)
    new_service_get_instructions_handler = partial(service_get_instructions_handler, db= dbc, bot=botc)

    dp.register_callback_query_handler(new_service_seller_start_handler, lambda c: "_buy_services_start_" in c.data, state="*")
    dp.register_message_handler(new_service_get_instructions_handler, state=buy_list.service_instruction)


    new_view_reviews = partial(view_reviews, db=dbc)
    dp.register_callback_query_handler(new_view_reviews, lambda c:c.data=="buyer_reviews", state=services_list.id)

    dp.register_callback_query_handler(new_accounts_kb_handler, lambda c: c.data.endswith("_offers"), state=services_list.cur_list)
    dp.register_callback_query_handler(new_account_by_one_handler, lambda c: c.data.startswith("ser_offer_id:"), state=services_list.cur_list)
    dp.register_callback_query_handler(new_buy_porcess_start_handler, lambda c: c.data == "buyer_buy", state=services_list.id)

    dp.register_callback_query_handler(new_chat_start_handler, lambda c: c.data == "buyer_chat", state=services_list.id)
    dp.register_callback_query_handler(new_delete_diamond_offer_handler, lambda c:c.data=="seller_delete", state=services_list.id)
    dp.register_callback_query_handler(new_back_buttons_handler, lambda c: c.data=="back_from_one", state=services_list.id)