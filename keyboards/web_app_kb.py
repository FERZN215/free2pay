from aiogram import types
from aiogram.types import ReplyKeyboardMarkup

def web_kb(data):
    param_kb = ReplyKeyboardMarkup(resize_keyboard=True)
    param_url = types.WebAppInfo(url = "https://192.168.31.184:8080/#/main?game="+str(data.get("game"))
                                 +"&pr_type="+str(data.get("game_type"))
                                 +"&server="+str(data.get("server"))
                                 +"&under_server="+str(data.get("under_server")))
    btn = types.MenuButtonWebApp("Предложения", web_app=param_url)
    param_kb.add(btn)
    
    return param_kb
