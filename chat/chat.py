from aiogram.dispatcher import FSMContext
from aiogram import types
from pymongo.database import Database
from aiogram.dispatcher.filters.state import State, StatesGroup
from bson.objectid import ObjectId

from aiogram import Bot, Dispatcher
from usefull.converters import chat_db_conver
from keyboards.chat_start import chat_start_kb, source_kb, stop_kb

from keyboards.menu import menu_kb

import os

class chat_states(StatesGroup):
    chat_ready = State()

async def chat_start(call:types.CallbackQuery, state:FSMContext, db:Database, bot:Bot):

    data = await state.get_data()
    if call.data.startswith("buyer_chat:"):
        deal = db["active_deals"].find_one({"_id":ObjectId(call.data.replace("buyer_chat:", ""))})
        offer = db[chat_db_conver(deal["game"])].find_one({"_id":deal["offer_id"]})
    else:
        offer = db[chat_db_conver(data.get("game"))].find_one({"_id":data.get("id")})
    target_id = offer["seller"]
    check_exist = db["chats"].find_one({"offer":offer["_id"]})

    if not check_exist:
        chat= {
            "offer":offer["_id"],
            "source":call.message.chat.id,
            "target":offer["seller"],
            "msgs":[]
        }
        db["chats"].insert_one(chat)
    else:
        chat = check_exist

    source = db["users"].find_one({"telegram_id":call.message.chat.id})
    await state.update_data(prev_state = await state.get_state(), target = target_id, source = call.message.chat.id, chat_id = chat["_id"])
    await chat_states.chat_ready.set()
    
    await call.message.answer("Подождем пока собеседник подключится к чату", reply_markup= source_kb(chat["_id"]))
    await bot.send_message(target_id, "C вами хочет начать диалог " + source["local_name"], reply_markup=chat_start_kb(chat["_id"]))

async def chat_start_process(call:types.CallbackQuery, state:FSMContext, db:Database, bot:Bot, dp:Dispatcher):
    data_mass = call.data.partition("_chat_")
    chat = db["chats"].find_one({"_id":ObjectId(data_mass[0])})
    match data_mass[2]:
        case "start":
            await state.update_data(prev_state = await state.get_state(), target = chat["target"], source =chat["source"], chat_id = chat["_id"])
            await chat_states.chat_ready.set()
            await call.message.answer("Диалог начался:", reply_markup=stop_kb)
            await bot.send_message(chat["source"], "Диалог начался", reply_markup=stop_kb)
        case "cancel":
            data = await state.get_data()
            await state.set_state(data.get("prev_state"))
            await state.update_data(prev_state = None)
            await call.message.answer("Диалог заверешен",reply_markup=menu_kb)
            if call.message.chat.id == chat["source"]:
                target_data = await dp.storage.get_data(chat=chat["target"])
                await dp.storage.set_state(chat = chat["target"], state = target_data.get("prev_state"))
                await dp.storage.update_data(chat=chat["target"], prev_state=None)
                await bot.send_message(chat["target"], "Диалог завершен",reply_markup=menu_kb)
            else:
                target_data = await dp.storage.get_data(chat=chat["source"])
                await dp.storage.set_state(chat = chat["source"], state = target_data.get("prev_state"))
                await dp.storage.update_data(chat=chat["source"], prev_state=None)
                await bot.send_message(chat["source"], "Диалог завершен", reply_markup=menu_kb)

async def message_process_handler(message:types.Message, state:FSMContext, db:Database, dp:Dispatcher, bot:Bot):
    data = await state.get_data()
    if message.text == "Стоп":
        
        
        await state.set_state(data.get("prev_state"))
        await state.update_data(prev_state = None)
        await message.answer("Диалог заверешен",reply_markup=menu_kb)
        chat = db["chats"].find_one({"_id":data.get("chat_id")})
        if message.chat.id == chat["source"]:
            target_data = await dp.storage.get_data(chat=chat["target"])
            await dp.storage.set_state(chat = chat["target"], state = target_data.get("prev_state"))
            await dp.storage.update_data(chat=chat["target"], prev_state=None)
            await bot.send_message(chat["target"], "Диалог завершен", reply_markup=menu_kb)
        else:
            target_data = await dp.storage.get_data(chat=chat["source"])
            await dp.storage.set_state(chat = chat["source"], state = target_data.get("prev_state"))
            await dp.storage.update_data(chat=chat["source"], prev_state=None)
            await bot.send_message(chat["source"], "Диалог завершен",reply_markup=menu_kb)
        
        return

    
    if message.chat.id == data.get("target"):
        if message.photo:
            print("here")
            photo_buf_id = ""
            for photo in message.photo:
                if photo_buf_id == photo.file_unique_id[:4]:
                    break

                photo_buf_id = photo.file_unique_id[:4]
                
                await message.photo[len(message.photo)-1].download('photos/'+str(photo.file_unique_id)+'.jpg')
                print(photo.file_unique_id)
                _photo = open('photos/'+str(photo.file_unique_id)+'.jpg', 'rb')
                await bot.send_photo(data.get("source"), _photo, reply_markup=stop_kb)
                os.remove('photos/'+str(photo.file_unique_id)+'.jpg')
                
            if message.caption:
                await bot.send_message(data.get("source"), "Отправил:\n"+message.caption, reply_markup=stop_kb)
            elif message.text:
                await bot.send_message(data.get("source"), "Отправил:\n"+message.text, reply_markup=stop_kb)
        else:
            await bot.send_message(data.get("source"),"Отправил:\n"+message.text , reply_markup=stop_kb)
    else:
        if message.photo:
            print("here")
            photo_buf_id = ""
            for photo in message.photo:
                if photo_buf_id == photo.file_unique_id[:4]:
                    break

                photo_buf_id = photo.file_unique_id[:4]
                await message.photo[len(message.photo)-1].download('photos/'+str(photo.file_unique_id)+'.jpg')
                print(photo.file_unique_id)
                _photo = open('photos/'+str(photo.file_unique_id)+'.jpg', 'rb')
                await bot.send_photo(data.get("target"), _photo, reply_markup=stop_kb)
                os.remove('photos/'+str(photo.file_unique_id)+'.jpg')
                
            if message.caption:
                await bot.send_message(data.get("target"), "Отправил:\n"+message.caption, reply_markup=stop_kb)
            elif message.text:
                await bot.send_message(data.get("target"), "Отправил:\n"+message.text, reply_markup=stop_kb)
        else:
            await bot.send_message(data.get("target"),"Отправил:\n"+message.text, reply_markup=stop_kb )

    

    if message.chat.id == data.get("target"):
        db["chats"].update_one({"_id":data.get("chat_id")}, {"$push":{"msgs":{"from":data.get("target"), "to":data.get("source"), "text":message.text}}})
    else:
        db["chats"].update_one({"_id":data.get("chat_id")}, {"$push":{"msgs":{"from":data.get("source"), "to":data.get("target"), "text":message.text}}})
    




