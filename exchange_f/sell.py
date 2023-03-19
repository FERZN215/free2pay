from aiogram.dispatcher import FSMContext
from aiogram import types



from games.l2m.category_manager import l2m_cat_sell_manage





async def sell_init_process(call:types.CallbackQuery, state:FSMContext):
    data = await state.get_data()
    match data.get("game"):
        case "game_lage2m":
            await l2m_cat_sell_manage(call, state)
        
