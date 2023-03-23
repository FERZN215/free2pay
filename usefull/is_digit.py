def is_digit(in_string:str):
    string = in_string.replace(',', '.')
    if string.isdigit():
       return True
    else:
        try:
            float(string)
            return True
        except ValueError:
            
            return False