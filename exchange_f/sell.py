from aiogram.dispatcher import FSMContext
from aiogram import types




from .sell_f.wallet.diamonds import diamonds_count
from .sell_f.services import services_name
from .sell_f.accounts import account_type
from .sell_f.things import thing_type







async def sell_init_process(call:types.CallbackQuery, state:FSMContext):
    data = await state.get_data()
    match data.get("game_type"):
        case "cat_diamonds":
            await diamonds_count(call, state)
        case "cat_services":
            await services_name(call, state)
        case "cat_accounts":
            await account_type(call, state)
        case "cat_things":
            await thing_type(call, state)
            
        case "cat_adena":
            await diamonds_count(call, state)
        case "cat_chaos":
            await services_sell(call, state)
        case "cat_divans":
            await accounts_sell(call, state)
        case "cat_ekza":
            await diamonds_count(call, state)
        case "cat_gil":
            await services_sell(call, state)
        case "cat_gold":
            await accounts_sell(call, state)
        case "cat_silver":
            await diamonds_count(call, state)
        case "cat_boost":
            await services_sell(call, state)
        case "cat_builds":
            await accounts_sell(call, state)
        case "cat_destiny_pve":
            await diamonds_count(call, state)
        case "cat_destiny_pvp":
            await services_sell(call, state)
        case "cat_donat":
            await accounts_sell(call, state)
        case "cat_expedition":
            await diamonds_count(call, state)
        case "cat_keys":
            await services_sell(call, state)
        case "cat_sbor":
            await accounts_sell(call, state)
        case "cat_timecards":
            await services_sell(call, state)
        case "cat_wow_pve":
            await accounts_sell(call, state)
        case "cat_wow_pvp":
            await accounts_sell(call, state)
            




async def services_sell(call:types.CallbackQuery, state:FSMContext):
    return








async def accounts_sell(call:types.CallbackQuery, state:FSMContext):
    return

