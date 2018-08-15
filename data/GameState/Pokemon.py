
from ..util import string_parse

class Pokemon():
    def __init__(self, pokeDict, nameDict, itemDict, abilDict, moveDict):
        self.nameDict = nameDict
        self.itemDict = itemDict
        self.abilDict = abilDict
        self.moveDict = moveDict
        self.pokeDict = pokeDict

        self.name = ""
        self.pokeNum = -1

        self.level = -1

        self.genderStr = ""
        self.gender = -1

        self.currHP = -1
        self.maxHP = -1

        self.isActive = None

        self.atk = -1
        self.spa = -1
        self.defense = -1
        self.spd = -1
        self.spe = -1

        self.moveList = []
        self.moveNumList = []

        self.abil = ""
        self.abilNum = -1

        self.item = ""
        self.itemNum = -1

        self.fainted = False

        self.hasSub = False

        self.parse_poke_dict()


    def parse_poke_dict(self):
        details = self.pokeDict["details"]
        details = details.split(", ")

        name = details[0]
        level = details[1]

        if len(details) == 3:
            gender = details[2]
            self.genderStr = gender.lower()
            self.gender = 0 if self.genderStr == "f" else 1
        else:
            self.genderStr = ""
            self.gender = -1

        print("Creating Pokemon obj: %s" % name)

        self.name = string_parse(name)
        self.pokeNum = self.nameDict[self.name]

        level = level.replace("L", "")
        self.level = int(level)

        self.maxHP = self.pokeDict["condition"].split("/")[1]
        self.currHP = self.maxHP

        self.isActive = self.pokeDict["active"]

        statDict = self.pokeDict["stats"]
        self.atk =     statDict["atk"]
        self.spa =     statDict["spa"]
        self.defense = statDict["def"]
        self.spd =     statDict["spd"]
        self.spe =     statDict["spe"]

        for move in self.pokeDict["moves"]:
            move = string_parse(move, stripNum=True)

            self.moveList.append(move)
            self.moveNumList.append(self.moveDict[move])
        
        self.abil = self.pokeDict["ability"]
        self.abilNum = self.abilDict[self.abil]

        self.item = self.pokeDict["item"]

        if self.item == "":
            self.itemNum = -1
        else:
            self.itemNum = self.itemDict[self.item]
    
    def set_health(self, val):
        self.currHP = val
        
        if self.currHP == 0:
            self.fainted = True


class Move():
    def __init__(self, name, moveDict):
        self.name = name
        
        self.maxPP = moveDict["pp"]
        self.priority = moveDict["priority"]
        
