from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


lineage_2m = InlineKeyboardButton('Lineage 2M', callback_data='game_lage2m')
world_of_warcraft = InlineKeyboardButton('World of Warcraft', callback_data='game_wow')
lineage_2 = InlineKeyboardButton('Lineage 2', callback_data='game_lage2')
lineage_2_essence = InlineKeyboardButton('Lineage 2 Essence', callback_data='game_lage2e')
lineage_2_classic = InlineKeyboardButton('Lineage 2 Classic', callback_data='game_lage2c')
lineage_2_free = InlineKeyboardButton('Lineage 2 Free', callback_data='game_lage2free')
albion_online = InlineKeyboardButton('Albion Online', callback_data='game_albion')
path_of_exiles = InlineKeyboardButton('Path of Exiles', callback_data='game_PoE')
new_world = InlineKeyboardButton('New World', callback_data='game_new_world')
aion_classic = InlineKeyboardButton('Aion Classic', callback_data='game_aion')
final_fantasy14 = InlineKeyboardButton('Final Fantasy XIV', callback_data='game_ff14')
destiny_2 = InlineKeyboardButton('Destiny 2', callback_data='game_destiny2')

back = InlineKeyboardButton('Назад', callback_data='back_games')

games_kb = InlineKeyboardMarkup().add(lineage_2m, world_of_warcraft, lineage_2).add(lineage_2_essence, lineage_2_classic, lineage_2_free).add(albion_online,path_of_exiles,new_world).add(aion_classic, final_fantasy14, destiny_2)





