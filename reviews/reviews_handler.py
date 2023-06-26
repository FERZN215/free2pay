from aiogram.dispatcher import FSMContext
from aiogram import types
from pymongo.database import Database
from aiogram import Dispatcher
from functools import partial



from .reviews import *
from .reviews_add import *


async def view_one_review_handler(call:types.CallbackQuery, state:FSMContext, db:Database):
    await call.message.delete()
    await view_one_review(call, state, db)

async def review_kb_process_handler(call:types.CallbackQuery, state:FSMContext, db:Database):
    await review_kb_process(call, state, db)



async def text_process_handler(message:types.Message, state:FSMContext):
    await text_process(message, state)

async def num_process_handler(message:types.Message, state:FSMContext, db:Database):
    await num_process(message, state, db)

#reviews_add_cancel

def reviews_handlers(dp:Dispatcher, dbc:Database):
    new_view_reviews = partial(view_reviews, db = dbc)
    new_view_one_review_handler = partial(view_one_review_handler, db = dbc)
    new_review_kb_process_handler = partial(review_kb_process_handler, db = dbc)

    new_num_process_handler = partial(num_process_handler, db=dbc)


    dp.register_callback_query_handler(new_view_one_review_handler, lambda c:c.data.startswith("review_id:"), state=review_list.review_list)
    dp.register_callback_query_handler(new_view_reviews, lambda c:c.data == "back_from_review", state=review_list.review_list)
    dp.register_callback_query_handler(new_review_kb_process_handler, lambda c:c.data.endswith("_reviews"), state =review_list.review_list)

    dp.register_callback_query_handler(reviews_add_cancel, lambda c: c.data == "cancel_add_review", state=reviews_add_states.review)

    dp.register_message_handler(text_process_handler, state=reviews_add_states.review)
    dp.register_message_handler(new_num_process_handler, state=reviews_add_states.num)
