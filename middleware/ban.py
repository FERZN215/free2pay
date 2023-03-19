from aiogram import types
from aiogram.dispatcher.handler import CancelHandler
from aiogram.dispatcher.middlewares import BaseMiddleware

class ban_user(BaseMiddleware):
    def __init__(self, col):
        super().__init__()
        self.collection = col

    async def on_pre_process_update(self, update:types.Update, data:dict):
        id = update.message.chat.id if update.message else update.callback_query.id
        answer = update.message.answer_video if update.message else update.callback_query.message.answer_video
        user = self.collection.find_one({"telegram_id":id})
        if user and user["status"] == "Banned":
            video = open('./media_content/ban.mp4', 'rb')
            await answer(video)
            raise CancelHandler()
        else:
            return
