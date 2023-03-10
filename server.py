from bot import bot
from flask import Flask, request
import asyncio

app = Flask(__name__)

@app.route('/send-message', methods=['POST'])
def handler():
   # получаем текст сообщения из запроса

    async def send_message():
        print("1",request.form.get("secret_key"))
        await bot.send_message(chat_id=1030297121, text="smth")
        
    asyncio.run(send_message())
    
    return 'Сообщение отправлено!'


app.run()