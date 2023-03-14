def com_sw(commission:str):
    return "+" if commission.replace("commission_", "") == "yes" else "-"