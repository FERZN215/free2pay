def com_sw(commission:str):
    return "+" if commission.replace("comission_", "") == "yes" else "-"
