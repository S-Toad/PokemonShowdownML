
def string_parse(nameStr, stripNum=False):
    nameStr = nameStr.lower()
    nameStr = nameStr.replace("'", "")
    nameStr = nameStr.replace("-", "")
    nameStr = nameStr.replace(" ", "")
    nameStr = nameStr.replace(".", "")

    if not stripNum:
        return nameStr

    numStr = "0123456789"

    for num in numStr:
        if num in nameStr:
            nameStr = nameStr.replace(num, "")

    return nameStr
