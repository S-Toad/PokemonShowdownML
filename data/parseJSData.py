import os
import pickle
from enum import Enum


def main():
    base_path = os.path.join(os.path.dirname(__file__), "JS_DATA")

    abilityDict = stripFile(base_path, "abilities", 43, '": {', False)
    moveDict = stripFile(base_path, "moves", 33, '": {', True)
    pokeDict = stripFile(base_path, "pokedex", 4, ": {", False)
    itemDict = stripFile(base_path, "items", 4, '": {', False)

    base_path = os.path.join(os.path.dirname(__file__), "obj")

    savePickle(base_path, abilityDict, "abilities")
    savePickle(base_path, moveDict, "moves")
    savePickle(base_path, pokeDict, "pokedex")
    savePickle(base_path, itemDict, "items")


def stripFile(base_path, fileName, startLine, checkString, isMoveJS):
    fileName = fileName + ".js"
    jsFile = open(os.path.join(base_path, fileName))
    fileDict = {}

    currVal = None
    for line_num, line in enumerate(jsFile):
        if line_num < startLine:
            continue
        
        if currVal is not None:
            if "num:" in line and "spritenum" not in line: 
                num = line.replace("\t\tnum: ", "")
                num = num.replace(",\n", "")

                if isMoveJS:
                    fileDict[currVal] = {"num": int(num)}
                else:
                    fileDict[currVal] = int(num)
                    currVal = None
            elif isMoveJS:
                if "pp:" in line and "pp" not in fileDict[currVal].keys():
                    pp = line.replace("\t\tpp: ", "")
                    pp = pp.replace(",\n", "")
                    fileDict[currVal]["pp"] = int(pp)
                elif "type:" in line:
                    moveType = line.replace("\t\ttype: ", "")
                    moveType = moveType.replace(",\n", "")
                    moveType = moveType.replace('"', '')

                    fileDict[currVal]["type"] = moveType.lower()
                    currVal = None
            continue
        
        if checkString in line and "}" not in line:
            currVal = line.replace(": {", "")
            currVal = currVal.replace('"', '')
            currVal = currVal.replace("\t", "")
            currVal = currVal.replace("\n", "")
    
    return fileDict


class DATA_TYPE(Enum):
    ABIL_DICT = 1
    MOVE_DICT = 2
    POKE_DICT = 3
    ITEM_DICT = 4


def savePickle(base_path, dictVar, name):
    with open(os.path.join(base_path, name + ".pkl"), "wb") as f:
        pickle.dump(dictVar, f, pickle.HIGHEST_PROTOCOL)

def getPickle(dateType):
    base_path = os.path.join(os.path.dirname(__file__), "obj")

    file_name = {
        DATA_TYPE.ABIL_DICT: "abilities.pkl",
        DATA_TYPE.MOVE_DICT: "moves.pkl",
        DATA_TYPE.POKE_DICT: "pokedex.pkl",
        DATA_TYPE.ITEM_DICT: "items.pkl"
    }[dateType]

    with open(os.path.join(base_path, file_name), "rb") as f:
        return pickle.load(f)

if __name__ == "__main__":
    main()