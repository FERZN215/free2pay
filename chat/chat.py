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


async def chat_start(call: types.CallbackQuery, state: FSMContext, db: Database,dp:Dispatcher, bot: Bot):
    data = await state.get_data()
    if call.data.startswith("buyer_chat:"):
        deal = db["active_deals"].find_one({"_id": ObjectId(call.data.replace("buyer_chat:", ""))})
        offer = db[chat_db_conver(deal["game"])].find_one({"_id": deal["offer_id"]})
        target_id = offer["seller"]

    elif "_m_buyer_cha_" in call.data:
        
        try:
            
            data_mass = call.data.partition("_m_buyer_cha_")
            offer = db[chat_db_conver(data_mass[0])].find_one({"_id": ObjectId(data_mass[2])})
            chat = db["chats"].find_one({"offer": offer["_id"]})
            print(offer)
        except TypeError:
            
            data_mass = call.data.partition("_m_buyer_cha_")
            offer = db["active_deals"].find_one({"offer_id": ObjectId(data_mass[2])})
            chat = db["chats"].find_one({"offer":offer["offer_id"]})
            
        


        if chat["target"] == call.message.chat.id:
            target_id = chat["source"]
        else:
            target_id = chat["target"]

        await state.finish()

    else:
        offer = db[chat_db_conver(data.get("game"))].find_one({"_id": data.get("id")})
        target_id = offer["seller"]


    if not chat:

        check_exist = db["chats"].find_one({"offer": offer["_id"]})

        if not check_exist:
            chat = {
                "offer": offer["_id"],
                "game": chat_db_conver(offer["game"]),
                "source": call.message.chat.id,
                "target": offer["seller"],
                "msgs": []
            }
            db["chats"].insert_one(chat)
        else:
            chat = check_exist

    source = db["users"].find_one({"telegram_id": call.message.chat.id})
    

    n_t_d = await call.message.answer("Подождем пока собеседник подключится к чату", reply_markup=source_kb(chat["_id"]))

    await state.update_data(prev_state=await state.get_state(), target=chat["target"], source=chat["source"],
                            chat_id=chat["_id"], need_to_del = n_t_d.message_id)
    await chat_states.chat_ready.set()

    s_n_t_d = await bot.send_message(target_id, "C вами хочет начать диалог " + source["local_name"],
                           reply_markup=chat_start_kb(chat["_id"]))
    
    await dp.storage.update_data(chat=target_id, need_to_del = s_n_t_d.message_id)
    
    


async def chat_start_process(call: types.CallbackQuery, state: FSMContext, db: Database, bot: Bot, dp: Dispatcher):
    data_mass = call.data.partition("_chat_")
    chat = db["chats"].find_one({"_id": ObjectId(data_mass[0])})
    if await state.get_state() == "chat_states:chat_ready":
        if call.message.chat.id == chat["target"]:
            await call.message.answer("Закончи свой текущий диалог, либо ты можешь отменить запрос")
            return

    match data_mass[2]:
        case "start":
            if chat["_id"] not in db["users"].find_one({"telegram_id": call.message.chat.id})["chats"]:
                db["users"].update_one({"telegram_id": call.message.chat.id}, {"$push": {"chats": chat["_id"]}})

            if chat["_id"] not in db["users"].find_one({"telegram_id": chat["source"]})["chats"]:
                db["users"].update_one({"telegram_id": chat["source"]}, {"$push": {"chats": chat["_id"]}})

            
            
            await state.update_data(prev_state=await state.get_state(), target=chat["target"], source=chat["source"], chat_id=chat["_id"])
            await chat_states.chat_ready.set()
            await call.message.answer("Диалог начался:", reply_markup=stop_kb)
            if call.message.chat.id == chat["target"]:
                target_data = await dp.storage.get_data(chat=chat["source"])

                await bot.delete_message(chat["source"], target_data.get("need_to_del"))
             
                await bot.send_message(chat["source"], "Диалог начался:", reply_markup=stop_kb)
            else:
                target_data = await dp.storage.get_data(chat=chat["target"])
            
                await bot.delete_message(chat["target"], target_data.get("need_to_del"))
            
                await bot.send_message(chat["target"], "Диалог начался:", reply_markup=stop_kb)
        case "cancel":
            data = await state.get_data()
            
            if data.get("prev_state"):
                await state.set_state(data.get("prev_state"))
                await state.update_data(prev_state=None)
            else:
                await state.finish()
            await call.message.answer("Диалог заверешен", reply_markup=menu_kb)
            if call.message.chat.id == chat["source"]:
                
                target_data = await dp.storage.get_data(chat=chat["target"])
                if(target_data.get("prev_state")):
                    
                    await dp.storage.set_state(chat=chat["target"], state=target_data.get("prev_state"))
                    await dp.storage.update_data(chat=chat["target"], prev_state=None)
                else:
                    
                    await dp.storage.finish(chat= chat["target"])

                await bot.delete_message(chat["target"], target_data.get("need_to_del"))
                await bot.send_message(chat["target"], "Диалог завершен", reply_markup=menu_kb)
            else:
                
                target_data = await dp.storage.get_data(chat=chat["source"])
                if target_data.get("prev_state"):
                    
                    await dp.storage.set_state(chat=chat["source"], state=target_data.get("prev_state"))
                    await dp.storage.update_data(chat=chat["source"], prev_state=None)
                else:
                    
                    await dp.storage.finish(chat= chat["source"])
                await bot.delete_message(chat["source"], target_data.get("need_to_del"))
                await bot.send_message(chat["source"], "Диалог завершен", reply_markup=menu_kb)


async def message_process_handler(message: types.Message, state: FSMContext, db: Database, dp: Dispatcher, bot: Bot):
    data = await state.get_data()
    

    
    if message.text == "Стоп":
        if data.get("msg_mass") and len(data.get("msg_mass")) > 0:
            for id in data.get("msg_mass"):
                await bot.delete_message(message.chat.id, id)

        if message.chat.id == data.get("target"):
            another_data = await dp.storage.get_data(chat=data.get("source"))
            if another_data.get("msg_mass") and len(another_data.get("msg_mass")) > 0:
                for id in another_data.get("msg_mass"):
                    await bot.delete_message(data.get("source"), id)
        else:
            another_data = await dp.storage.get_data(chat=data.get("target"))
    
            if another_data.get("msg_mass") and len(another_data.get("msg_mass")) > 0:
                for id in another_data.get("msg_mass"):
                    await bot.delete_message(data.get("target"), id)

        
        if data.get("prev_state"):
            await state.set_state(data.get("prev_state"))
        else:
            await state.finish()

        
        await state.update_data(prev_state=None, msg_mass = None, target = None, source = None)
        await message.answer("Диалог заверешен", reply_markup=menu_kb)
        chat = db["chats"].find_one({"_id": data.get("chat_id")})
        if message.chat.id == chat["source"]:
            target_data = await dp.storage.get_data(chat=chat["target"])
            if target_data.get("prev_state"):
                await dp.storage.set_state(chat=chat["target"], state=target_data.get("prev_state"))
            else:
                await dp.storage.finish(chat=chat["target"])
            await dp.storage.update_data(chat=chat["target"], prev_state=None, msg_mass = None, target = None, source = None)
            await bot.send_message(chat["target"], "Диалог завершен", reply_markup=menu_kb)
        else:
            target_data = await dp.storage.get_data(chat=chat["source"])
            if target_data.get("prev_state"):
                await dp.storage.set_state(chat=chat["source"], state=target_data.get("prev_state"))
            else:
                await dp.storage.finish(chat=chat["source"])
            await dp.storage.update_data(chat=chat["source"], prev_state=None, msg_mass = None, target = None, source = None)
            await bot.send_message(chat["source"], "Диалог завершен", reply_markup=menu_kb)
        return

    if message.chat.id == data.get("target"):
        
        another_data = await dp.storage.get_data(chat=data.get("source"))
        if await dp.storage.get_state(chat=data.get("source")) != "chat_states:chat_ready" or another_data.get("target") != data.get("target") or another_data.get("source") != data.get("source"):
            return
        
        
    else:
        
        another_data = await dp.storage.get_data(chat=data.get("target"))
        if await dp.storage.get_state(chat=data.get("target")) != "chat_states:chat_ready" or another_data.get("target") != data.get("target") or another_data.get("source") != data.get("source"):
            return
        
       

    
    if data.get("msg_mass"):
        n_l_mass = data.get("msg_mass")
        n_l_mass.append(message.message_id)
        await state.update_data(msg_mass = n_l_mass)
    else:
        await state.update_data(msg_mass = [message.message_id])

    if message.chat.id == data.get("target"):

        target_data = await dp.storage.get_data(chat=data.get("source"))

        

        if message.photo:
            photo_buf_id = ""
            for photo in message.photo:
                if photo_buf_id == photo.file_unique_id[:4]:
                    break

                photo_buf_id = photo.file_unique_id[:4]

                await message.photo[len(message.photo) - 1].download('photos/' + str(photo.file_unique_id) + '.jpg')
                
                _photo = open('photos/' + str(photo.file_unique_id) + '.jpg', 'rb')
                await bot.send_photo(data.get("source"), _photo, reply_markup=stop_kb)
                os.remove('photos/' + str(photo.file_unique_id) + '.jpg')

            if message.caption:
                msg = await bot.send_message(data.get("source"), "Отправил:\n" + message.caption, reply_markup=stop_kb)
            elif message.text:
                msg = await bot.send_message(data.get("source"), "Отправил:\n" + message.text, reply_markup=stop_kb)
                
        else:
            msg = await bot.send_message(data.get("source"), "Отправил:\n" + message.text, reply_markup=stop_kb)

        if msg:
            if target_data.get("msg_mass"):
                n_mass = target_data.get("msg_mass")
                n_mass.append(msg.message_id)
                await dp.storage.update_data(chat= data.get("source"), msg_mass = n_mass)
            else:
                await dp.storage.update_data(chat=data.get("source"), msg_mass =  [msg.message_id])

        
    else:

        target_data = await dp.storage.get_data(chat=data.get("target"))

        

        if message.photo:
   
            photo_buf_id = ""
            for photo in message.photo:
                if photo_buf_id == photo.file_unique_id[:4]:
                    break

                photo_buf_id = photo.file_unique_id[:4]
                await message.photo[len(message.photo) - 1].download('photos/' + str(photo.file_unique_id) + '.jpg')
                
                _photo = open('photos/' + str(photo.file_unique_id) + '.jpg', 'rb')
                await bot.send_photo(data.get("target"), _photo, reply_markup=stop_kb)
                os.remove('photos/' + str(photo.file_unique_id) + '.jpg')

            if message.caption:
                msg = await bot.send_message(data.get("target"), "Отправил:\n" + message.caption, reply_markup=stop_kb)
            elif message.text:
                msg = await bot.send_message(data.get("target"), "Отправил:\n" + message.text, reply_markup=stop_kb)
        else:
            msg = await bot.send_message(data.get("target"), "Отправил:\n" + message.text, reply_markup=stop_kb)

        if msg:
            if target_data.get("msg_mass"):
                n_mass = target_data.get("msg_mass")
                n_mass.append(msg.message_id)
                await dp.storage.update_data(chat= data.get("target"), msg_mass = n_mass)
            else:
                await dp.storage.update_data(chat=data.get("target"), msg_mass =  [msg.message_id])



    if message.chat.id == data.get("target"):
        db["chats"].update_one({"_id": data.get("chat_id")}, {"$push": {"msgs": {"from": data.get("target"), "to": data.get("source"), "text": message.text}}})
    else:
        db["chats"].update_one({"_id": data.get("chat_id")}, {
            "$push": {"msgs": {"from": data.get("source"), "to": data.get("target"), "text": message.text}}})
        
  
