from aiogram.dispatcher import FSMContext
from aiogram import types

async def buy_init_process(call:types.CallbackQuery, state:FSMContext):
    return