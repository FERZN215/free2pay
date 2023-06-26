from bot import bot, db
from flask import Flask, request
import asyncio
from bson import ObjectId
from usefull.converters import game_converter
app = Flask(__name__)
key = "123"
@app.route('/newmsg', methods=['POST'])
def handler():
   
    async def send_message():
        data = request.get_json()
        chat = db["chats"].find_one({"_id": ObjectId(data["chat_id"])})
        src = db["users"].find_one({"telegram_id": chat["source"]})
        target = db["users"].find_one({"telegram_id": chat["target"]})
        await bot.send_message(chat_id=chat["source"], text='Админ ответил в диалоге c: '+target["local_name"]+"\n<b>"+chat["msgs"][len(chat["msgs"])-1]["text"]+"</b>", parse_mode='HTML')
        
        await bot.send_message(chat_id=chat["target"], text='Админ ответил в диалоге c: '+src["local_name"]+"\n<b>"+chat["msgs"][len(chat["msgs"])-1]["text"]+"</b>", parse_mode='HTML')

    asyncio.run(send_message())
    
    return 'Сообщение отправлено!'



@app.route('/deal_change', methods=['POST'])
def deal_handler():
   
    async def deal_change():
        data = request.get_json()
        data = data["deal"]
        print(data)
        await bot.send_message(chat_id=data["buyer"], text='Админ внес измемения в сделку по товару\n<b>'+
                               game_converter(data["game"], data["category"])+"\nПродавец: "+
                               db["users"].find_one({"telegram_id": data["seller"]})["local_name"]+"</b>", parse_mode='HTML')
        
        await bot.send_message(chat_id=data["seller"], text='Админ внес измемения в сделку по товару\n<b>'+
                               game_converter(data["game"], data["category"])+"\nПокупатель: "+
                               db["users"].find_one({"telegram_id": data["buyer"]})["local_name"]+"</b>", parse_mode='HTML')

    asyncio.run(deal_change())
    
    return 'Сообщение отправлено!'


app.run()