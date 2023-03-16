from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram import types
from pymongo.database import Database
from keyboards.exchange import games_kb
from .buy import buy_init_process
from .sell import sell_init_process


from keyboards.l2m.l2m_servers import l2m_servers
from keyboards.l2m.l2m_under_servers import l2m_under_servers
from keyboards.l2m.l2m_category import l2m_category_kb

class exchange_states(StatesGroup):
    type = State()
    game = State()
    game_type = State()
    server = State()
    under_server = State()


async def exchange_process(message:types.Message, state:FSMContext):
    await state.update_data(type=message.text)
    await message.answer('Выбери игру из перечисленных:', reply_markup=games_kb)
    await exchange_states.game.set()


async def category_process(call: types.CallbackQuery, state: FSMContext):
    await state.update_data(game=call.data)
    await exchange_states.game_type.set()
    #МЕГА ТРАБЛ, НУЖНО РАСПИСАТЬ КАЖДУЮ ИГРУ ДЛЯ ВЫВОДА ПОДКАТЕГОРИИ
    data = await state.get_data()
    match data.get('game'):
        case "game_lage2m":
            need_kb = l2m_category_kb

    await call.message.answer('Выбери подкатегорию', reply_markup=need_kb)


        

async def init_process(call: types.CallbackQuery, state: FSMContext, db:Database):
    data = await state.get_data()
    match data.get('type'):
        case "Купить":
            await buy_init_process(call, state, db)
        case "Продать":
            await sell_init_process(call, state)



async def server_process(call:types.CallbackQuery, state:FSMContext, red = False):
    if red == False:
        await state.update_data(game_type=call.data)
    data = await state.get_data()
    match data.get('game'):
        case 'game_lage2m':
            nkb = l2m_servers

    await exchange_states.server.set()
    await call.message.answer("Выбери сервер:", reply_markup=nkb)


async def next_server_process(call:types.CallbackQuery, state:FSMContext, db:Database):
    await state.update_data(server = call.data)
    data = await state.get_data()
    match data.get('game'):
        case 'game_lage2m':
            nkb = l2m_under_servers
            await exchange_states.under_server.set()
            await call.message.answer("Выбери подсервер:", reply_markup=nkb)
            return
        
    await init_process(call, state, db)


async def under_server_process(call:types.CallbackQuery, state:FSMContext, db:Database):
    await state.update_data(under_server = call.data)
    await init_process(call, state, db)
   