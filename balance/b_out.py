from aiogram.dispatcher import FSMContext
from aiogram import types
from pymongo.database import Database
from aiogram.dispatcher.filters.state import State, StatesGroup
from keyboards.menu import menu_kb
from usefull.is_digit import is_digit

class balance_out_states(StatesGroup):
    sum_out = State()

async def balance_out_sum(message:types.Message, state:FSMContext):
    await balance_out_states.sum_out.set()
    await message.answer("Введи сумму для вывода:")

async def balance_out_process(message:types.Message, state:FSMContext, db:Database):
    if not is_digit(message.text):
        await message.reply("Сумма должна быть написана числом")
        return
    if float(message.text.replace(',', '.')) > db["users"].find_one({"telegram_id":message.chat.id})["balance"]:
        await message.answer("Недостаточно средств:")
        return
    
    db["users"].update_one({"telegram_id":message.chat.id}, {"$inc":{"balance":-float(message.text.replace(',', '.'))}})
    await state.finish()
    await message.answer("Средвства выведены",reply_markup=menu_kb)