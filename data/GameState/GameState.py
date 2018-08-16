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
    
    def add_pokemon_to_enemy(self, pokeName):
        pass
    
    def handle_main_action(self, action, params):
        
        if action == ActionType.MOVE:
            self.handle_move(params)
        elif action == ActionType.SWITCH:
            self.handle_switch(params)
        elif action == ActionType.NEW_TURN:
            turn = params[2]
            print("-----------------------------------\nTurn %s starting" % turn)
    
    def handle_sub_action(self, mainAction, action, params):
        
        if mainAction == ActionType.MOVE:
            pass
            #self.handle_sub_move(action, params)

                
    def get_pokemon(self, team, pokeName):
        for poke in team:
            if poke.name in pokeName:
                return poke
        return None


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
        teamID, pokeName = pokeString.split("a: ")
        pokeName = string_parse(pokeName)

        return (teamID, pokeName)
    

    def handle_move(self, params):
        self.actionParms = params

        teamID, pokeName = self.strip_team(params[2])
        moveUsed = string_parse(params[3])

        poke = None
        if teamID == self.id:
            poke = self.get_pokemon(self.team, pokeName)
        else:
            poke = self.get_pokemon(self.enemyTeam, pokeName)
            if moveUsed not in poke.pokeMoveDict.keys():
                print("%s not seen before by this pokemon" % moveUsed)
                poke.add_move(moveUsed)

        print("%s pp decreased" % moveUsed)
        poke.pokeMoveDict[moveUsed]["curr_pp"] -= 1


    
    def handle_sub_move(self, action, params):
        usedPokeName = self.actionParms[2]
        moveUsed = self.actionParms[3]
        targetPokeName = self.actionParms[4]

        p1ID, usedPokeName = self.strip_team(usedPokeName)
        p2ID, targetPokeName = self.strip_team(targetPokeName)
        moveAgainstItself = p1ID == p2ID

        if action == ActionType.DAMAGE:
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
                    if targetPokeName in poke.name:
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

    def handle_switch(self, params):
        print(params)
        teamID, pokeName = self.strip_team(params[2])

        if teamID == self.id:
            for poke in self.team:
                poke.isActive = poke.name in pokeName

                if poke.name in pokeName:
                    print("%s on your team is now set to active" % poke.name)
        else:
            foundPokemon = False
            for poke in self.enemyTeam:
                if poke.name in pokeName:
                    print("%s on enemy team set to active" % poke.name)
                    poke.isActive = True
                    foundPokemon = True
                else:
                    poke.isActive = False
            
            if not foundPokemon:
                poke = Pokemon(None, self.nameDict, self.itemDict, self.abilDict, self.moveDict)
                poke.parse_pokemon_info(params[2], params[3])
                poke.maxHP = self.currHP = 1.0
                poke.isActive = True

                print("%s created for enemy team" % poke.name)

                self.enemyTeam.append(poke)

    def print_team(self, team):
        print("-----------------------")
        for poke in team:
            print("Pokemon: %s" % poke.name)
            print("Moves: ")
            print(poke.pokeMoveDict)
            print("\n")
        