from aiogram.dispatcher import FSMContext
from aiogram import types, Bot
from pymongo.database import Database
from aiogram.dispatcher.filters.state import State, StatesGroup
from bson.objectid import ObjectId

from keyboards.my_chats import my_chats_kb, one_chat_kb
from keyboards.menu import menu_kb

class mychats_states(StatesGroup):
    chat_list = State()
    id = State()

async def chats_list(message:types.Message, state:FSMContext, db:Database):
    await mychats_states.chat_list.set() 
    await state.update_data(chat_list = 10)

    user = db["users"].find_one({"telegram_id":message.chat.id})
   
    if len(user["chats"]) <= 0:
        await message.answer("У вас нет чатов(", reply_markup=menu_kb)
        await state.finish()
        return

    await message.answer("Чаты:", reply_markup=my_chats_kb(user["chats"][:11], 10, message.chat.id, db))


async def chats_kb_process(call:types.CallbackQuery, state:FSMContext, db:Database):
    data = await state.get_data()
    user = db["users"].find_one({"telegram_id": call.message.chat.id})
    match call.data.replace("_chats", ""):

        case "history":
            await state.update_data(chat_list = 10, d_history = True)
            await call.message.edit_reply_markup(my_chats_kb(user["chats"][:11], 10, call.message.chat.id, db, True))
            return

        case "active":
            await state.update_data(chat_list = 10, d_history = False)
            await call.message.edit_reply_markup(my_chats_kb(user["chats"][:11], 10, call.message.chat.id, db))
            return

        case "forward":
            _cur_list = data.get("chat_list") + 10
            _chats = user["chats"][data.get("chat_list"): _cur_list+1]
            
        case "back":
            _cur_list = data.get("chat_list") - 10
            _chats = user["chats"][_cur_list-10:_cur_list+1]

        case "cancel":
            await call.message.delete()
            await state.finish()
            return
        
    await state.update_data(chat_list = _cur_list)

    if data.get("d_history"):
        await call.message.edit_reply_markup(my_chats_kb(_chats, _cur_list, call.message.chat.id, db, True))
    else:
        await call.message.edit_reply_markup(my_chats_kb(_chats, _cur_list, call.message.chat.id, db))



async def one_chat(call:types.CallbackQuery, state:FSMContext, db:Database):
    chat = db["chats"].find_one({"_id":ObjectId(call.data.replace("my_chmat_id:", ""))})
    
    target = db["users"].find_one({"telegram_id":chat["target"]})
    source = db["users"].find_one({"telegram_id":chat["source"]})
   
    await mychats_states.id.set()
    text = ""
    for msg in chat["msgs"]:

        if msg["text"]:
        
            if msg["from"] == target["telegram_id"]:
                text+="От: "+ target["local_name"] + "\n" + "Кому: " + source["local_name"] + "\nТекст:"
            else:
                text+="От: "+ source["local_name"] + "\n" + "Кому: " + target["local_name"] + "\nТекст:"
            
            
            text += msg["text"] + "\n---------------\n"
        
    if len(chat["msgs"]) > 0:
        await call.message.answer(text, reply_markup=one_chat_kb(chat["offer"], chat["game"]))
    else:
        await call.message.answer("Пустой диалог")
        await chats_list(call.message, state, db)

