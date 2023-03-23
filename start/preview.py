from aiogram import types
from pymongo.database import Database
from keyboards.preview import preview_kb
from keyboards.menu import menu_kb




async def preview(message:types.Message, db:Database):
    collection = db["users"]
    if collection.find_one({"telegram_id":message.chat.id}):
        await message.answer("С возвращением. Фарми, зарабатывай, покупай", reply_markup=menu_kb)
    else:
        photo = open('./media_content/preview.jpg', 'rb')
        await message.answer_photo(photo, "Свободная биржа игровых ценностей. Фарми, зарабатывай, покупай", reply_markup=preview_kb)
