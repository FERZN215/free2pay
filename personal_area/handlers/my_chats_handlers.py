from aiogram.dispatcher import FSMContext
from aiogram import types
from pymongo.database import Database
from aiogram import Dispatcher
from functools import partial

from chat.chat import chat_start

from ..my_chats import *



async def chats_kb_process_handler(call:types.CallbackQuery, state:FSMContext, db:Database):
    await chats_kb_process(call, state, db)

async def one_chat_handler(call:types.CallbackQuery, state:FSMContext, db:Database):
    await call.message.delete()
    await one_chat(call, state, db)

async def chats_list_handler(call:types.CallbackQuery, state:FSMContext, db:Database):
    await call.message.delete()
    await chats_list(call.message, state, db)

async def start_chat_handler(call:types.CallbackQuery, state:FSMContext, db:Database,dp:Dispatcher, bot:Bot):
    await call.message.delete()
    await chat_start(call, state, db,dp, bot)

def my_chats_handlers(dp:Dispatcher, dbc:Database, botc:Bot):

    new_chats_kb_process_handler = partial(chats_kb_process_handler, db=dbc)
    new_one_chat_handler = partial(one_chat_handler, db = dbc)
    new_chats_list_handler = partial(chats_list_handler, db=dbc )
    new_start_chat_handler = partial(start_chat_handler, db=dbc, bot=botc, dp=dp)

    dp.register_callback_query_handler(new_one_chat_handler, lambda c:c.data.startswith("my_chmat_id:"), state=mychats_states.chat_list)
    dp.register_callback_query_handler(new_chats_kb_process_handler, lambda c:c.data.endswith("_chats"), state =mychats_states.chat_list)
    dp.register_callback_query_handler(new_start_chat_handler, lambda c: "_m_buyer_cha_" in c.data, state=mychats_states.id )
    dp.register_callback_query_handler(new_chats_list_handler, lambda c:c.data == "back_to_one_chat", state=mychats_states.id)
    
