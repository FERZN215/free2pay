from aiogram.dispatcher import FSMContext
from aiogram import types
from pymongo.database import Database
from aiogram.dispatcher.filters.state import State, StatesGroup
from keyboards.menu import menu_kb
from usefull.is_digit import is_digit


class balance_add_states(StatesGroup):
    sum = State()

async def balance_add_summ(message:types.Message, state:FSMContext):
    await balance_add_states.sum.set()
    await message.answer("Введи сумму пополнения в рублях:")

async def balance_add(message:types.Message, state:FSMContext, db:Database):
    if not is_digit(message.text):
        await message.reply("Сумму нужно указать числом:")
        return
    
    await state.update_data(sum = float(message.text.replace(',', '.')))
    db["users"].update_one({"telegram_id":message.chat.id}, {"$inc":{"balance":float(message.text.replace(',', '.'))}})
    await state.finish()
    await message.answer("Пополнил)",reply_markup=menu_kb)