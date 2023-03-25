from aiogram.dispatcher import FSMContext
from aiogram import types
from pymongo.database import Database
from aiogram import Dispatcher
from functools import partial



from chat.chat import *

async def chat_start_process_handler(call:types.CallbackQuery, state:FSMContext, db:Database,bot:Bot, dp:Dispatcher):
    await call.message.delete()
    await chat_start_process(call, state, db, bot, dp)

async def message_process_handler_handler(message:types.Message, state:FSMContext, db:Database,dp:Dispatcher, bot:Bot):
    await message_process_handler(message, state, db,dp, bot)


def chat_handlers(dp:Dispatcher, db:Database, bot:Bot):
    new_chat_start_process_handler = partial(chat_start_process_handler, db=db, bot=bot, dp=dp)
    new_message_process_handler_handler = partial(message_process_handler_handler, db=db,dp=dp, bot=bot)

    dp.register_callback_query_handler(new_chat_start_process_handler, lambda c: "_chat_" in c.data, state="*")
    dp.register_message_handler(new_message_process_handler_handler, state=chat_states.chat_ready, content_types=types.ContentType.all())
