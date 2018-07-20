

class Pokemon():
    def __init__(self, nameDict, itemDict, abilDict, moveDict):
        self.nameDict = nameDict
        self.itemDict = itemDict
        self.abilDict = abilDict
        self.moveDict = moveDict

        self.pokeName = ""
        self.pokeNum = -1
        self.movesName = ["", "", "", ""]
        self.movesNum = [-1, -1, -1, -1]
        self.level = -1
        self.maxHP = -1
        self.abilName = ""
        self.abilNum = -1
        self.itemName = ""
        self.itemNum = -1

        self.currHP = -1

    def setData(self, pokeDict):
        details = pokeDict["details"].split(",")

        name = details[0].lower()
        level = details[1].replace("L", "")
        maxHp = pokeDict["condition"].split("/")[1]
        active = pokeDict["active"]
        stats = pokeDict["stats"] # TODO: Add stats
        moves = pokeDict["moves"]
        ability = pokeDict["ability"]
        item = pokeDict["item"]

        self.setName(name)
        for move in moves:
            self.setMove(move)
        self.setItem(item)
        self.setLevel(level)
        self.setMaxHP(maxHp)
        self.setAbil(ability)
    
    def setName(self, pokeName):
        self.pokeName = self.simplifyStr(pokeName)
        self.pokeNum = self.nameDict[self.pokeName]


    def setMove(self, moveString):
        for x in range(0,4):
            if self.movesName[x] != "":
                continue
            
            moveName = ''.join(x for x in moveString if not x.isdigit())
            
            self.movesName[x] = moveName
            self.movesNum[x] = self.moveDict[moveName]
            break

    def setAbil(self, abilName):
        self.abilName = abilName
        self.abilNum = self.abilDict[self.abilName]

    def setItem(self, itemName):
        self.itemName = itemName
        self.itemNum = self.itemDict[self.itemName]

    def setLevel(self, levelString):
        self.level = int(levelString)
    
    def setMaxHP(self, hpString):
        self.maxHP = int(hpString)
        self.currHP = self.maxHP

    def diffHP(self, amount):
        self.currHP += amount

        if self.currHP > self.maxHP:
            self.currHP = self.maxHP
        elif self.currHP < 0:
            self.currHP = 0
    
    def simplifyStr(self, string):
        string = string.lower()
        string = string.replace(" ", "")
        string = string.replace("-", "")

        return string

    def print(self):
        print("Pokemon: %s | %d" % (self.pokeName, self.pokeNum))
        print("Level: %d" % self.level)
        print("Max HP: %d" % self.maxHP)
        print("Ability: %s | %d" % (self.abilName, self.abilNum))
        print("Item: %s | %d" % (self.itemName, self.itemNum))
        print("Moves: ")
        print(self.movesName)
        print("Moves Num: ")
        print(self.movesNum)
