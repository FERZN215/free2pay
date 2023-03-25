from aiogram.dispatcher import FSMContext
from aiogram import types
from pymongo.database import Database
from aiogram.dispatcher.filters.state import State, StatesGroup


from ..keyboards.l2m_acc_cat import l2m_account_cat
from keyboards.sell_conf import sell_conf_kb
from keyboards.menu import menu_kb

from usefull.is_digit import is_digit
from usefull.add_warn import add_warn
from usefull.converters import ac_t_t
class accounts_states(StatesGroup):
    acc_type = State()
    level = State()
    cost = State()
    description = State()
    photos = State()



async def account_type(call:types.CallbackQuery, state:FSMContext):
    await accounts_states.acc_type.set()
    await call.message.answer("Пожалуйста выберите класс",reply_markup=l2m_account_cat)

async def account_level(call:types.CallbackQuery, state:FSMContext):
    await state.update_data(acc_type = call.data)
    await accounts_states.level.set()
    await call.message.answer("Пожалуйста укажите уровень аккаунта:")


async def account_cost(message:types.Message, state:FSMContext):
    if message.text.isdigit() and 1<= int(message.text) <= 99:
        await state.update_data(level = int(message.text))
        await accounts_states.cost.set()
        await message.answer("Пожалуйста укажите цену аккаунта:")
    else:
        await message.answer("Уровень аккаунта должен быть целым числом, повтори попытку:")

async def account_description(message:types.Message, state:FSMContext):
    if not is_digit(message.text):
        await message.answer("Цена должна быть числом, повтори попытку:")
        return

    await state.update_data(cost = float(message.text.replace(',', '.')))
    await accounts_states.description.set()
    await message.answer("Напиши описание своему аккаунту одним сообщением до 200 символов:")

async def accounts_screenshots(message:types.Message, state:FSMContext):
    if len(message.text) > 200: 
        await message.answer("Описание должно быть меньше 200 символов, повтори попытку:")
        return
    await state.update_data(description = message.text)
    await accounts_states.photos.set()
    await message.answer("Отправь ссылку на свои изображения(поддерживается только imgur)")

async def accounts_check(message:types.Message, state:FSMContext, db:Database):
    if not message.text.startswith("https://imgur.com/"):
        await message.answer("Чую подвох, попробуй ещё раз")
        await add_warn(message.chat.id, db)
        return
    await state.update_data(photos = message.text)
    data = await state.get_data()
    await message.answer(
        "Класс: " + str(ac_t_t(data.get("acc_type"))) + "\n" +
        "Уровень: " + str(data.get("level")) + "\n" +
        "Цена: " + str(data.get("cost")) + "\n" +
        "Описание: " + str(data.get("description")) + "\n" +
        "Ссылка на фотографии: " +str( data.get("photos")),  reply_markup=sell_conf_kb
    )

    
async def account_db_set(call: types.CallbackQuery, state: FSMContext, db: Database):
    data = await state.get_data()
    db["l2m"].insert_one({
        "game": data.get("game"), 
        "pr_type":data.get("game_type"),
        "server": data.get("server"), 
        "under_server": data.get("under_server"),
        "seller": call.message.chat.id,
        "class" : data.get("acc_type") ,
        "level" : data.get("level"),
        "cost" : data.get("cost"),
        "description" : data.get("description"),
        "photos" :  data.get("photos"),
        "invis": False
    })
    await state.finish()
    await call.message.answer("Твое предложения видно всем!", reply_markup=menu_kb)
