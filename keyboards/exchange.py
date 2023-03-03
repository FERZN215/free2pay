from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

lineage_2m = InlineKeyboardButton('Lineage 2M', callback_data='game_lage2m')
world_of_warcraft = InlineKeyboardButton('World of Warcraft', callback_data='game_wow')
lineage_2 = InlineKeyboardButton('Lineage 2', callback_data='game_lage2')
lineage_2_essence = InlineKeyboardButton('Lineage 2 Essence', callback_data='game_lage2e')
lineage_2_classic = InlineKeyboardButton('Lineage 2 Classic', callback_data='game_lage2c')
albion_online = InlineKeyboardButton('Albion Online', callback_data='game_albion')
path_of_exiles = InlineKeyboardButton('Path of Exiles', callback_data='game_PoE')
new_world = InlineKeyboardButton('New World', callback_data='game_new_world')
aion_classic = InlineKeyboardButton('Aion Classic', callback_data='game_aion')
back = InlineKeyboardButton('Назад', callback_data='back')

games_kb = InlineKeyboardMarkup().add(aion_classic, albion_online, lineage_2, lineage_2m) .row(lineage_2_classic, lineage_2_essence).row(new_world, path_of_exiles, world_of_warcraft).row(back)

accounts = InlineKeyboardButton('Аккаунты', callback_data='cat_accounts')
diamonds = InlineKeyboardButton('Алмазы', callback_data='cat_diamonds')
coins = InlineKeyboardButton('Монеты', callback_data='cat_coins')
services = InlineKeyboardButton('Услуги', callback_data='cat_services')


category_kb = InlineKeyboardMarkup().add(accounts, diamonds).row(coins, services)




