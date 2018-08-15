from .Pokemon import Pokemon
from enum import Enum
import copy
import ast
from data.logdata import get_action_type, ActionType
from ..util import string_parse

class GameState():
    def __init__(self, requestString, nameDict, itemDict, abilDict, moveDict):
        print("Initializing GameState")
        
        self.nameDict = nameDict
        self.itemDict = itemDict
        self.abilDict = abilDict
        self.moveDict = moveDict

        self.actionParms = None

        teamJSON = requestString.split("|request|")[1]
        teamJSON = teamJSON.replace("\\", "")
        teamJSON = teamJSON[:-1]
        teamJSON = teamJSON.replace("true", "True")
        teamJSON = teamJSON.replace("false", "False")
        teamJSON = teamJSON.replace("null", "None")

        print("------------------------")
        print(teamJSON)
        print("------------------------")
        
        teamDict = ast.literal_eval(teamJSON)

        self.id = teamDict["side"]["id"]
        self.enemyId = "p1" if self.id == "p2" else "p2"

        self.team = []
        self.enemyTeam = []

        #print(teamDict["side"]["pokemon"])
        for pokeDict in teamDict["side"]["pokemon"]:
            self.team.append(Pokemon(
                pokeDict, nameDict, itemDict, abilDict, moveDict
            ))

    def next_state(self):
        pass
    
    def handle_main_action(self, action, params):
        
        if action == ActionType.MOVE:
            self.actionParms = params
            return
        elif action == ActionType.NEW_TURN:
            turn = params[2]
            print("-----------------------------------\nTurn %s starting" % turn)
    
    def handle_sub_action(self, mainAction, action, params):
        
        if mainAction == ActionType.MOVE:
            usedPokeName = self.actionParms[2]
            moveUsed = self.actionParms[3]
            targetPokeName = self.actionParms[4]

            p1ID, usedPokeName = self.strip_team(usedPokeName)
            p2ID, targetPokeName = self.strip_team(targetPokeName)
            moveAgainstItself = p1ID == p2ID

            if action == ActionType.DAMAGE:
                usedPokeName = string_parse(usedPokeName)
                targetPokeName = string_parse(targetPokeName)
                moveUsed = string_parse(moveUsed)

                damageDone = params[3].split(" ")[0]
                
                damageFrom = None
                if len(params) == 5:
                    damageFrom = params[4]
                    damageFrom = damageFrom.split("[from] ")[1]

                if self.id == p1ID:
                    print("Moved used against enemy")
                    pass
                else:
                    if damageFrom is None:
                        print("%s used %s against %s setting to %s" % (usedPokeName, moveUsed, targetPokeName, damageDone))
                    else:
                        print("%s at %s from %s" % (targetPokeName, damageDone, damageFrom))
                    for poke in self.team:
                        if targetPokeName == poke.name:
                            print("Setting %s health" % poke.name)
                            poke.currHP = poke.set_health(int(damageDone.split("/")[0]))

                            if moveAgainstItself:
                                if moveUsed == "substitute":
                                    poke.substitute = True
            elif action == ActionType.BOOST or action == ActionType.UNBOOST:
                statType = params[3]
                amount = params[4]

                print("%s boosted/unboosted %s to %s" % (targetPokeName, statType, amount))

                if self.id == p1ID:
                    poke = self.get_pokemon(self.team, targetPokeName)
                else:
                    pass # they used
            else:
                print("ELSE %s" % action)
                print("%s used %s against %s" % (usedPokeName, moveUsed, targetPokeName))

                
    def get_pokemon(self, team, pokeName):
        for poke in team:
            if poke.name == pokeName:
                return poke


    def parse_round(self, validTurnData):
        mainAction = None

        for turnData in validTurnData:
            for line in turnData.split("\\n"):
                actionTuple = get_action_type(line)

                if actionTuple == None:
                    continue
                
                aType, action = actionTuple
                params = line.split("|")

                if aType == ActionType.MAIN:
                    mainAction = action
                    self.handle_main_action(action, params)
                elif aType == ActionType.SUB:
                    self.handle_sub_action(mainAction, action, params)
                else:
                    print("ERROR ACTION NOT HANDLED")
        return self

    def strip_team(self, pokeString):
        return tuple(pokeString.split("a: "))
    
    def handle_move(self, actionLog):
        pass
    
    def handle_switch(self, actionLog):
        pass
