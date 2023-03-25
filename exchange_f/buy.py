from aiogram.dispatcher import FSMContext
from aiogram import types
from pymongo.database import Database

from games.l2m.category_manager import l2m_cat_buy_manage

async def buy_init_process(call:types.CallbackQuery, state:FSMContext, db:Database):
    data = await state.get_data()
    match data.get("game"):
        case "game_lage2m":
            await l2m_cat_buy_manage(call, state, db)
            


