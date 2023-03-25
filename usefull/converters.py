def game_converter(game:str, type:str):
    match game:
        case "game_lage2m":
            match type:
                case "cat_accounts":
                    return "Игра: Lineage 2M|Тип товара: Аккаунты"
                case "cat_diamonds":
                    return "Игра: Lineage 2M|Тип товара: Алмазы"
                case "cat_things":
                    return "Игра: Lineage 2M|Тип товара: Предметы"
                case "cat_services":
                    return "Игра: Lineage 2M|Тип товара: Услуги"

def server_converter(server:str):
    match server:
        case "server_l2m_zighard":
            return "Сервер: Зигхард"
        case "server_l2m_barc":
            return "Сервер: Барц"
        case "server_l2m_leona":
            return "Сервер: Леона"
        case "server_l2m_erika":
            return "Сервер: Эрика" 

def under_server_converter(under_server: str):
    match under_server:
        case "under_s_l2m_1":
            return "Подсервер 1"
        case "under_s_l2m_2":
            return "Подсервер 2"
        case "under_s_l2m_3":
            return "Подсервер 3"
        case "under_s_l2m_4":
            return "Подсервер 4"
        case "under_s_l2m_5":
            return "Подсервер 5"
        case "under_s_l2m_6":
            return "Подсервер 6"         
        
def things_to_text(type:str):
    cur_type = type.replace("things_", "")
    match cur_type:
        case "weapon":
            return "Оружие"
        case "armor":
            return "Броня"
        case "accessories":
            return "Аксессуары"
        case "other":
            return "Прочее"
        

def ac_t_t(type:str):
    match type:
        case "account_orb":
            return "Орб"
        case "account_posox":
            return "Посох"
        case "account_kinj":
            return "Кинжал"
        case "account_luk":
            return "Лук"
        case "account_arbal":
            return "Арбалет"
        case "account_dual":
            return "Дуалы"
        case "account_shield":
            return "Щит"
        case "account_glefa":
            return "Глефа"
        case "account_double_sword":
            return "Двуручный меч"

        