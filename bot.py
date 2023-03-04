from aiogram import Bot, Dispatcher, executor
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram import types
from pymongo import MongoClient

from middleware.ban import ban_user
from config import BOT_TOKEN, MONGO_API

from start.preview import preview
from start.registration import *
from exchange.exchange import *
from personal_area.reviews import reviews_process
from personal_area.deals import deals_process



client = MongoClient(MONGO_API)
db = client["test_db"]

bot = Bot(token=BOT_TOKEN)
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)

ban_middleware = ban_user(db['users'])
dp.middleware.setup(ban_middleware)

@dp.message_handler(commands=['start'])
async def start(message: types.Message):
    await preview(message, db)

@dp.callback_query_handler(lambda c: c.data == "registration")
async def registration_handler(call: types.CallbackQuery):
    await call.message.delete()
    await license_agreement(call.message)

@dp.callback_query_handler(lambda c: c.data.startswith('license_'))
async def license_agreement_handler(call: types.CallbackQuery):
    await license_agreement_process(call, db)
    await call.message.delete()

@dp.message_handler(state= registration_states.nickname)
async def nickname_handler(message:types.Message, state:FSMContext):
    await password(message, state)

@dp.message_handler(state= registration_states.password)
async def password_handler(message:types.Message, state:FSMContext):
    await password_process(message, state, db)


@dp.callback_query_handler(lambda c: c.data == "buy" or c.data == "sell")
async def exchange_handler(call: types.CallbackQuery, state: FSMContext):
    await call.message.delete()
    await exchange_process(call,state)


@dp.callback_query_handler(lambda c: c.data.startswith("game_"), state=exchange_states.game)
async def category_handler(call:types.CallbackQuery, state: FSMContext):
    await call.message.delete()
    await category_process(call, state)

@dp.callback_query_handler(lambda c: c.data.startswith("cat_"), state=exchange_states.game_type)
async def init_handler(call: types.CallbackQuery, state: FSMContext):
    await call.message.delete()
    await init_process(call, state)
    await state.finish() #Удалить перед модификацией

@dp.message_handler()
async def reviews_handler(message:types.Message):
    match message.text:
        case "Профиль":
            await personal_area(message, db)
        case "Отзывы":
            await reviews_process(message, db)
        case "Сделки":
            await deals_process(message, db)



if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)