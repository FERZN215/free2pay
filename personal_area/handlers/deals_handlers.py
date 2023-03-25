from aiogram.dispatcher import FSMContext
from aiogram import types
from pymongo.database import Database
from aiogram import Dispatcher
from functools import partial



from ..deals import *



async def deals_kb_process_handler(call:types.CallbackQuery, state:FSMContext, db:Database):
    await deals_kb_process(call, state, db)

async def one_active_deal_handler(call:types.CallbackQuery, state:FSMContext, db:Database):
    await call.message.delete()
    await one_active_deal(call, state, db)


async def manage_deal_handler(call:types.CallbackQuery, state:FSMContext, db:Database, bot:Bot):
    await call.message.delete()
    await manage_deal(call, state, db, bot)

def active_deals_handlers(dp:Dispatcher, dbc:Database, botc:Bot):

    new_manage_deal_handler = partial(manage_deal_handler, db=dbc, bot=botc)
    new_deals_kb_process_handler = partial(deals_kb_process_handler, db = dbc)
    new_one_active_deal_handler = partial(one_active_deal_handler, db = dbc)

    dp.register_callback_query_handler(new_one_active_deal_handler, lambda c:c.data.startswith("active_deal_id:"), state=active_deals_list.deal_list)
    dp.register_callback_query_handler(new_deals_kb_process_handler, lambda c:c.data.endswith("_deals"), state =active_deals_list.deal_list)
    dp.register_callback_query_handler(new_manage_deal_handler, lambda c: "_one_" in c.data, state=active_deals_list.id)
