from aiogram import Bot, Dispatcher, executor
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.webhook import *
from aiogram import types
from pymongo import MongoClient
from middleware.ban import ban_user
from config import BOT_TOKEN, MONGO_API

from start.preview import preview
from start.registration import *
from exchange_f.exchange import *

from personal_area.deals import deals_process, active_deals_list
from personal_area.handlers.deals_handlers import active_deals_handlers
from personal_area.handlers.my_chats_handlers import my_chats_handlers
from personal_area.my_chats import chats_list

from balance.b_add import *
from balance.b_out import *


from games.l2m.sell.handlers.services_handlers import services_sell_handlers
from games.l2m.sell.handlers.diamonds_handler import diamonds_sell_handlers
from games.l2m.sell.handlers.accounts_handler import accounts_sell_handlers
from games.l2m.sell.handlers.things_handler import things_sell_handlers



from games.l2m.buy.handlers.diamonds_buy_handler import diamonds_buy_handlers
from games.l2m.buy.handlers.accounts_buy_handler import accounts_buy_handler
from games.l2m.buy.handlers.services_buy_handler import services_buy_handler
from games.l2m.buy.handlers.things_buy_handler import things_buy_handler
from games.l2m.buy.handlers.buy_handler import buy_handlers

from reviews.reviews_handler import reviews_handlers
from chat.chat_handlers import chat_handlers


# mas = [1,2,3,4,5,6,7,8,9,0,11,22,33,44,55,66,77,88,99,00]
# print(mas[3:10])

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

@dp.message_handler()
async def menu_handler(message:types.Message, state:FSMContext):
    match message.text:
        case "Профиль":
            await personal_area(message, db)
        case "Отзывы":
            return# await reviews_process(message, db)
        case "Активные сделки":
            await deals_process(message,state, db)
        case "Купить" | "Продать":
            await exchange_process(message, state)
        case "Пополнить":
            await balance_add_summ(message, state)
        case "Вывести":
            await balance_out_sum(message, state)
        case "Мои чаты":
            await chats_list(message, state, db)
    
@dp.message_handler(state= balance_out_states.sum_out)
async def balance_out_process_handler(message:types.Message, state:FSMContext):
    await balance_out_process(message, state, db)


@dp.message_handler(state= balance_add_states.sum)
async def balance_process(message:types.Message, state:FSMContext):
    await balance_add(message, state, db)

@dp.callback_query_handler(lambda c: c.data.startswith("game_"), state=exchange_states.game)
async def category_handler(call:types.CallbackQuery, state: FSMContext):
    await call.message.delete()
    await category_process(call, state)

@dp.callback_query_handler(lambda c: c.data.startswith("cat_"), state=exchange_states.game_type)
async def server_handler(call: types.CallbackQuery, state: FSMContext):
    await call.message.delete()
    await server_process(call, state)

@dp.callback_query_handler(lambda c: c.data.startswith("server_"), state=exchange_states.server)
async def next_server_handler(call: types.CallbackQuery, state: FSMContext):
    await call.message.delete()
    await next_server_process(call, state, db)

@dp.callback_query_handler(lambda c: c.data.startswith("under_s_"), state=exchange_states.under_server)
async def under_server_handler(call: types.CallbackQuery, state: FSMContext):
    await call.message.delete()
    await under_server_process(call, state, db)


@dp.callback_query_handler(lambda c: c.data == "back_from_deals", state=active_deals_list.id)
async def back_from_deals_handler(call:types.CallbackQuery, state:FSMContext):
    await call.message.delete()
    await deals_process(call.message, state, db)

#--------------------------------------------------------------------------------------------------------------------------



services_sell_handlers(dp, db)
diamonds_sell_handlers(dp, db)
accounts_sell_handlers(dp, db)
things_sell_handlers(dp, db)


#--------------------------------------------------------------------------------------------------------------------------


diamonds_buy_handlers(dp, db, bot)
accounts_buy_handler(dp, db, bot)
services_buy_handler(dp, db, bot)
things_buy_handler(dp, db, bot)
buy_handlers(dp, db, bot)
reviews_handlers(dp, db)
active_deals_handlers(dp, db, bot)

#--------------------------------------------------------------------------------------------------------------------------
chat_handlers(dp, db, bot)
my_chats_handlers(dp, db, bot)
            






if __name__ == '__main__':
    executor.start_polling(dispatcher=dp, skip_updates=True)
