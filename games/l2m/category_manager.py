from aiogram.dispatcher import FSMContext
from aiogram import types
from pymongo.database import Database


from .sell.accounts import account_type
from .sell.diamonds import diamonds_count
from .sell.things import thing_type
from .sell.services import services_name

from .buy.diamonds import diamonds_out, one_diamond_offer
from .buy.accounts import accounts_out, one_account_offer
from .buy.services import services_out, one_service_offer
from .buy.things import things_out, one_thing_offer




async def l2m_cat_sell_manage(call:types.CallbackQuery, state:FSMContext):
    data = await state.get_data()
    match data.get("game_type"):
        case "cat_accounts":
            await account_type(call, state)
        case "cat_diamonds":
            await diamonds_count(call, state)
        case "cat_things":
            await thing_type(call, state)
        case "cat_services":
            await services_name(call, state)


async def l2m_cat_buy_manage(call:types.CallbackQuery, state:FSMContext, db:Database):
    data = await state.get_data()
    match data.get("game_type"):
        case "cat_diamonds":
            await diamonds_out(call, state, db)
        case "cat_accounts":
            await accounts_out(call, state, db)
        case "cat_services":
            await services_out(call, state, db)
        case "cat_things":
            await things_out(call, state, db)

async def l2m_web_manager(message:types.Message, category, state:FSMContext, db:Database):
    match category:
        case "cat_diamonds":
            await one_diamond_offer(None, state, db, message )
        case "cat_accounts":
            await one_account_offer(None, state, db, True, message)
        case "cat_services":
            await one_service_offer(None, state, db, True, message)
        case "cat_things":
            await one_thing_offer(None, state, db, True, message)



