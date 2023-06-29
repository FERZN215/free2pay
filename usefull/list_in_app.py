from aiogram import types
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

def web_kb(data):
    param_kb = InlineKeyboardMarkup()
    param_url = types.WebAppInfo(url = "https://serene-capybara-913481.netlify.app/#/main?game="+str(data.get("game"))
                                 +"&pr_type="+str(data.get("game_type"))
                                 +"&server="+str(data.get("server"))
                                 +"&under_server="+str(data.get("under_server")))
    btn = types.MenuButtonWebApp("Офферы", web_app=param_url)
    param_kb.add(btn)
    print(param_url)
    return param_kb
