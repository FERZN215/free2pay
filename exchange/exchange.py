from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram import types

from keyboards.exchange import games_kb, category_kb
from .buy import buy_init_process
from .sell import sell_init_process

class exchange_states(StatesGroup):
    type = State()
    game = State()
    game_type = State()


async def exchange_process(call, state):
    await state.update_data(type=call.data)
    await call.message.answer('Выбери игру из перечисленных:', reply_markup=games_kb)
    await exchange_states.game.set()


async def category_process(call: types.CallbackQuery, state: FSMContext):
    await state.update_data(game=call.data)
    await exchange_states.game_type.set()
    await call.message.answer('Выбери подкатегорию', reply_markup=category_kb)


async def init_process(call: types.CallbackQuery, state: FSMContext):
    await state.update_data(game_type=call.data)
    data = await state.get_data()
    match data.get('type'):
        case "buy":
            await buy_init_process(call, state)
        case "sell":
            await sell_init_process(call, state)