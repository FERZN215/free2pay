def type_to_text(type:str):
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