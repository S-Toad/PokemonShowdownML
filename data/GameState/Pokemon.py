
from ..util import string_parse, parse_json
import ast
import copy

class Pokemon():
    def __init__(self, pokeDict, nameDict, itemDict, abilDict, moveDict):
        
        # Store dictionaries
        self.nameDict = nameDict
        self.itemDict = itemDict
        self.abilDict = abilDict
        self.moveDict = moveDict
        self.pokeDict = pokeDict

        # Set default values of pokemon features
        self.name = ""
        self.trueName = ""
        self.pokeNum = -1

        self.types = []
        self.possible_abilities = []

        self.level = -1

        self.genderStr = ""
        self.gender = -1

        self.currHP = -1
        self.maxHP = -1

        self.isActive = None

        self.stats = {
            "hp" : -1,
            "atk": -1,
            "spa": -1,
            "def": -1,
            "spd": -1,
            "spe": -1
        }

        self.statMultipliers = {
            "atk": 0,
            "spa": 0,
            "def": 0,
            "spd": 0,
            "spe": 0,
            "evasion": 0,
            "accuracy": 0
        }

        self.baseMultipliers = copy.deepcopy(self.statMultipliers)
        """
        self.atkMult = 0
        self.spaMult = 0
        self.defMult = 0
        self.spdMult = 0
        self.speMult = 0
        """

        self.pokeMoveDict = {}

        self.abil = ""
        self.abilNum = -1

        self.item = None
        self.itemNum = -1

        self.fainted = False

        if self.pokeDict is not None:
            self.parse_poke_dict()

        self.statuses = []
        self.statusesList = [
            'brn','par','slp',
            'frz','psn','tox',
            'confusion'
        ]

    def parse_pokemon_info(self, indentStr, detailStr):
        """Handles setting the name, level, and gender of a pokemon

        Input:
        * indentStr - String in format "pxa: pokeName"
        * detailStr - String in format "pokeName, LXY, GENDER"
        """

        # Example Strings
        # Indent - p2: Shaymin
        # Details - Shaymin-Sky, L73

        # Get level and gender out
        details = detailStr.split(", ")

        self.trueName = string_parse(details[0])

        # Get name
        name = indentStr.split(": ")[1]
        level = details[1]

        # True if pokemon has gender
        if len(details) == 3:
            gender = details[2]
            self.genderStr = gender.lower()
            self.gender = 0 if self.genderStr == "f" else 1
        else:
            self.genderStr = ""
            self.gender = -1
        
        # Simplify name
        self.name = string_parse(name)

        # Get pokemon
        self.pokeNum = int(self.nameDict[self.trueName]["num"])

        baseStats = self.nameDict[self.trueName]["baseStats"]
        baseStats = parse_json(baseStats)
        baseStatsDict = ast.literal_eval(baseStats)

        for key in self.stats.keys():
            self.stats[key] = int(baseStatsDict[key])

        self.types = self.nameDict[self.trueName]["types"]
        self.types = self.types.replace("[", "").replace("]", "")
        self.types = self.types.split(", ")

        abilityDict = self.nameDict[self.trueName]["abilities"]
        abilityDict = parse_json(abilityDict)
        print(abilityDict)

        abilityDict = ast.literal_eval(abilityDict)
        
        for value in abilityDict.values():
            self.possible_abilities.append(string_parse(value))

        # Set level
        level = level.replace("L", "")
        self.level = int(level)
    
    def add_move(self, moveStr):
        """Handles adding a move to a pokemon

        Input:
        * moveStr - The move name
        """

        # Strip the string including numbers
        moveStr = string_parse(moveStr, stripNum=True)

        print("%s move being added" % moveStr)

        # Find the data on the move
        moveDict = self.moveDict[moveStr]

        # Handles edge cases of hiddenpowers
        moveName = moveStr
        if "hiddenpower" in moveName:
            moveName = "hiddenpower"
        elif "struggle" == moveName:
            return

        # Set num, pp, and type of move
        self.pokeMoveDict[moveName] = {
            "num": int(moveDict["num"]),
            "max_pp": int(moveDict["pp"]),
            "curr_pp": int(moveDict["pp"]),
            "type": moveDict["type"]
        }

        # If the enemy used hidden power, we dont know the type
        if moveStr == "hiddenpower":
            self.pokeMoveDict[moveName]["type"] = ""
    
    def set_item(self, itemString):
        self.item = itemString

        if self.item == "":
            self.itemNum = -1
        else:
            self.itemNum = int(self.itemDict[self.item]["num"])

    def set_status(self, statusString):
        self.statuses.append(statusString)
    
    def remove_status(self, statusString):
        self.statuses.remove(statusString)

    def parse_poke_dict(self):
        """Handles the initial data dump at the beginning of a match
        """

        # Get identStr and detailsStr and set its features
        self.parse_pokemon_info(self.pokeDict["ident"], self.pokeDict["details"])

        # Set HP
        self.maxHP = self.pokeDict["condition"].split("/")[1]
        self.currHP = self.maxHP

        # Set if active
        self.isActive = self.pokeDict["active"]

        # Set stats
        self.stats = self.pokeDict["stats"]

        # Add moves
        for moveStr in self.pokeDict["moves"]:
            self.add_move(moveStr)
        
        # Set ability
        self.possible_abilities = [self.pokeDict["ability"]]

        # Set items (if any)
        self.set_item(self.pokeDict["item"])

    def set_health(self, val):
        """Handles seting health"""
        if self.fainted:
            return

        print("%s has its health set to %s" % (self.name, str(val)))

        # Set health
        self.currHP = val
        # Check if dead
        if self.currHP == 0:
            print("%s fainted" % self.name)
            self.fainted = True

    def set_stat_boost(self, statStr, amount):
        print("%s had its %s changed by %s" % (self.name, statStr, str(amount)))

        try:
            self.statMultipliers[statStr] += amount
        except:
            print(self.statMultipliers.keys())
            print("|" + statStr + "|")

        if self.statMultipliers[statStr] > 8:
            self.statMultipliers[statStr] = 8
        elif self.statMultipliers[statStr]  < -8:
            self.statMultipliers[statStr] = -8
    
    
    def print_details(self):
        print("Name: %s" % self.name)
        if self.name != self.trueName:
            print("True Name: %s" % self.trueName)
        
        print("Num: %s" % str(self.pokeNum))

        print("Level: %s" % str(self.level))

        print("Item: %s" % self.item)

        print("Gender: %s" % str(self.gender))
        
        print("Active: %s" % str(self.isActive))

        print("Moves: ", end='')
        print(self.pokeMoveDict)

        print("Type: ", end='')
        print(self.types)
        
        print("Stats: ", end='')
        print(self.stats)
        
        print("Health: %s/%s" % (str(self.currHP), str(self.maxHP)))
        
        print("Possible Abilities: ", end='')
        print(self.possible_abilities)

        print("Statuses: ", end='')
        print(self.statuses)

        print("Stat Mults: ", end='')
        print(self.statMultipliers)
