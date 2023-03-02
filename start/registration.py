from aiogram.dispatcher import FSMContext
from aiogram import types
from aiogram.dispatcher.filters.state import State, StatesGroup

from keyboards.license_agreement import license_agreement_kb

from start.preview import preview
from start.personal_area import personal_area


class registration_states(StatesGroup):
    nickname = State()
    password = State()


async def license_agreement(message: types.Message):
    await message.answer("Просим ознакомиться и принять принять лицензионное соглашение",
                         reply_markup=license_agreement_kb)


async def license_agreement_process(call: types.CallbackQuery, db):
    match call.data:
        case "license_no":
            await call.answer("Для использования биржи требуется принять лицензионное соглашение")
            await preview(call.message, db)
        case "license_yes":
            await registration_states.nickname.set()
            await call.message.answer("Отлично, давай придумаем никнейм, все таки анонимная биржа:")


async def password(message: types.Message, state: FSMContext):
    await state.update_data(nickname=message.text)
    await registration_states.password.set()
    await message.answer(
        "Запомнил! Теперь давай определимся с паролем для защиты твоего баланса. Помни, он должен быть длиннее 6 символов:")


async def password_process(message: types.Message, state: FSMContext, db):
    if len(message.text) < 6:
        await message.answer("Твой пароль должен состоять минимум из 6 символов")
    else:
        await state.update_data(password=message.text)
        await message.delete()
        data = await state.get_data()
        collection = db["users"]
        collection.insert_one(
            {"username": message.from_user.username, "local_name": data.get("nickname"), "telegram_id": message.chat.id,
             "password": data.get("password"), "status": "default", "balance": 0.00, "bill_id": "", "chats": [],
             "freeze_balance": [], "statistics": {"total": 0, "successful": 0, "arbitration": 0}, "reviews": []})
        await state.finish()
        await personal_area(message, db)
