from aiogram.dispatcher import FSMContext
from aiogram import types
from pymongo.database import Database
from aiogram import Dispatcher
from functools import partial

from start.personal_area import Profile

from ..my_reviews import *



async def view_one_review_handler(call:types.CallbackQuery, state:FSMContext, db:Database):
    await call.message.delete()
    await view_one_review(call, state, db)

async def review_kb_process_handler(call:types.CallbackQuery, state:FSMContext, db:Database):
    await review_kb_process(call, state, db)

async def view_reviews_handler(call:types.CallbackQuery, state:FSMContext, db:Database):
    await call.message.delete()
    await view_reviews(call, state, db)


def my_reviews_handlers(dp:Dispatcher, dbc:Database):

    new_view_reviews = partial(view_reviews, db = dbc)

    new_view_one_review_handler = partial(view_one_review_handler, db = dbc)

    new_review_kb_process_handler = partial(review_kb_process_handler, db = dbc)

    new_view_reviews_handler = partial(view_reviews_handler, db=dbc)

    dp.register_callback_query_handler(new_view_reviews_handler, lambda c: c.data == "all_reviews", state=Profile.profile)
    dp.register_callback_query_handler(new_view_one_review_handler, lambda c:c.data.startswith("review_id:"), state=my_review_list.my_review_list)
    dp.register_callback_query_handler(new_view_reviews, lambda c:c.data == "back_from_review", state=my_review_list.my_review_list)
    dp.register_callback_query_handler(new_review_kb_process_handler, lambda c:c.data.endswith("_reviews"), state =my_review_list.my_review_list)

