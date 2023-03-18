from pymongo.database import Database
async def add_warn(id:int, db:Database):
    user = db["users"].find_one({"telegram_id":id})
    
    if(user["warns"] + 1) >= 3:
        db["users"].update_one({"telegram_id":id}, {"$set":{"status":"Banned"}})

    db["users"].update_one({"telegram_id":id}, {"$set":{"warns":int(int(user["warns"]) + 1)}})
    