def getUsername(str: str) -> False or str:
    str = str.split("@")
    try:
        return str[1]
    except IndexError:
        return False
