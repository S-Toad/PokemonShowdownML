from .Pokemon import Pokemon
from enum import Enum
import copy
import ast
from data.logdata import get_action_type, ActionType
from ..util import string_parse

class GameState():
    def __init__(self, requestString, nameDict, itemDict, abilDict, moveDict):
        """GameState holds information concerning a match in a turn-to-turn basis

        Holds information concerning teams and field hazards
        """
        print("Initializing GameState")

        # Define lookup dictionaries for Pokemon Objects to have
        self.nameDict = nameDict
        self.itemDict = itemDict
        self.abilDict = abilDict
        self.moveDict = moveDict

        # Used by "Main" actions to pass its params to "sub" action
        self.actionParams = None

        self.teamJSON = requestString

        # Debug print of JSON
        print("------------------------")
        print(self.teamJSON)
        print("------------------------")
        
        # Evaluated edited JSON as python dictionary
        teamDict = ast.literal_eval(self.teamJSON)

        # Get teams IDs
        self.id = teamDict["side"]["id"]
        self.enemyId = "p1" if self.id == "p2" else "p2"

        # Empty list to hold information on Pokemon
        self.team = []
        self.enemyTeam = []

        # Create pokemon objects of our teams pokemon
        for pokeDict in teamDict["side"]["pokemon"]:
            self.team.append(Pokemon(
                pokeDict, nameDict, itemDict, abilDict, moveDict
            ))
        
        self.field = ""
        self.weather = ""
        self.hazards = {}
        self.enemyHazards = {}

        self.teamHasSub = False
        self.enemyHasSub = False



    def handle_main_action(self, action, params):
        """Handles the processing of "main" actions

        Main actions may include switch, using a move, or a new turn. This is first
        passed here to handle and possibly provide context to sub action handling

        Inputs:
        * action - ActionType Enum describing the event
        * params - A list of string parameters describing the event
        """
        if action == ActionType.MOVE:
            self.handle_move(params)
        elif action == ActionType.SWITCH or action == ActionType.DRAG:
            self.handle_switch(params)
        elif action == ActionType.FAINT:
            # []|faint|p2a: Heatran
            details = params[2]
            teamID, pokeName = self.strip_team(details) 
            poke = self.get_pokemon(None, pokeName, teamID=teamID)
            poke.set_health(0)
        elif action == ActionType.DETAILS_CHANGED:
            self.handle_details_changed(params)
        elif action == ActionType.NEW_TURN:
            turn = params[2]
            print("-----------------------------------\nTurn %s starting" % turn)
    

    def handle_sub_action(self, mainAction, action, params):
        """Similar to handle_main_action, handles the smaller events

        Sub events usually tie back to a main event. A move event may trigger
        a damage event which is handled here.

        Inputs:
        * mainAction - The overarching ActionType enum event
        * action - ActionType Enum describing the sub-event
        * params - A list of string parameters describing the sub-event
        """
        print(action)

        if action == ActionType.DAMAGE:
            damagedPokemonStr = params[2]
            healthStr = params[3]
            healthStr = healthStr.split(" ")[0]
            self.set_health(damagedPokemonStr, healthStr)
        elif action == ActionType.HEAL:
            # |-heal|p1a: Cryogonal|7/100|[from] item: Leftovers
            healedPokemonStr = params[2]
            healthStr = params[3]
            healthStr = healthStr.split(" ")[0]
            self.set_health(healedPokemonStr, healthStr)

            if len(params) < 5:
                return

            fromStr = params[4]
            print("From: %s" % fromStr)
        elif action == ActionType.STATUS:
            # []|-status|p1a: Dhelmise|tox
            details = params[2]
            teamID, pokeName = self.strip_team(details)
            poke = self.get_pokemon(None, pokeName, teamID=teamID)
            poke.set_status(params[3])
            print("%s inflicted with %s" % (poke.name, params[3]))
        elif action == ActionType.CURE_STATUS:
            #[]|-curestatus|p2a: Chansey|tox|[msg]
            details = params[2]
            teamID, pokeName = self.strip_team(details)
            poke = self.get_pokemon(None, pokeName, teamID=teamID)
            poke.remove_status(params[3])
            print("%s cured of %s" % (poke.name, params[3]))
        elif action == ActionType.BOOST or action == ActionType.UNBOOST:
            # []|-unboost|p1a: Deoxys|spa|2
            details = params[2]
            statType = params[3]
            amount = int(params[4])
            if action == ActionType.UNBOOST:
                amount = -1 * amount

            teamID, pokeName = self.strip_team(details)
            poke = self.get_pokemon(None, pokeName, teamID=teamID)

            poke.set_stat_boost(statType, amount)
        elif action == ActionType.FIELD_START:
            #[]|-fieldstart|move: Misty Terrain|
            terrain = params[3].split(": ")[1]
            self.field = string_parse(terrain)
            print("Terrain: %s started" % self.field)
        elif action == ActionType.FIELD_END:
            print("Terrain: %s ended" % self.field)
            self.field = ""
        elif action == ActionType.SIDE_START:
            # Example: []|-sidestart|p1: jkkjkjkjwq|move: Toxic Spikes
            #          []|-sidestart|p1: kkjkjwq|Spikes
            sideeffect = params[3]

            if ":" in sideeffect:
                sideeffect = sideeffect.split(": ")[1]
            sideeffect = string_parse(sideeffect)

            teamID = params[2].split(":")[0]

            if teamID == self.id:
                if sideeffect in self.hazards.keys():
                    self.hazards[sideeffect] += 1
                else:
                    self.hazards[sideeffect] = 1
                print("%s for my team now at %s" % (sideeffect, str(self.hazards[sideeffect])))
            else:
                if sideeffect in self.enemyHazards.keys():
                    self.enemyHazards[sideeffect] += 1
                else:
                    self.enemyHazards[sideeffect] = 1
                print("%s for enemy team now at %s" % (sideeffect, str(self.enemyHazards[sideeffect])))
        elif action == ActionType.SIDE_END:
            # Example: []|-sideend|p1: jkkjkjkjwq|move: Toxic Spikes|[of] p1a: Vileplume
            sideeffect = params[3].split(": ")[1]
            sideeffect = string_parse(sideeffect)

            teamID = params[2].split(":")[0]

            if teamID == self.id:
                print("%s ended for my team" % sideeffect)
                del self.hazards[sideeffect]
            else:
                print("%s ended for enemy team" % sideeffect)
                del self.enemyHazards[sideeffect]
        elif action == ActionType.WEATHER:
            #[]|-weather|RainDance
            weatherEffect = params[2]
            if weatherEffect == "RainDance" or weatherEffect == "Drizzle":
                weatherEffect = "rain"
            elif weatherEffect == "none":
                weatherEffect = ""
            else:
                weatherEffect = string_parse(weatherEffect)
            
            if self.weather != weatherEffect:
                print("%s weather beginning" % weatherEffect)
                self.weather = weatherEffect
        elif action == ActionType.ITEM:
            # []|-item|p2a: Bewear|Choice Scarf|[from] move: Switcheroo
            teamID, pokeName = self.strip_team(params[2])
            itemStr = string_parse(params[3])

            poke = self.get_pokemon(None, pokeName, teamID=teamID)
            poke.set_item(itemStr)

            print("%s now has %s" % (poke.name, itemStr))
        elif action == ActionType.END_ITEM:
            #[]|-enditem|p2a: Dialga|Leftovers|[from] move: Knock Off|[of] p1a: Landorus
            teamID, pokeName = self.strip_team(params[2])
            poke = self.get_pokemon(None, pokeName, teamID=teamID)
            poke.set_item("")
        elif action == ActionType.ABILITY:
            print(params)
            # []|-ability|p1a: Arcanine|Intimidate|boost
            teamID, pokeName = self.strip_team(params[2])
            abilityName = string_parse(params[3])
            poke = self.get_pokemon(None, pokeName, teamID=teamID)

            if len(poke.possible_abilities) == 1:
                return

            poke.possible_abilities = [abilityName]
            print("%s known to have: %s" % (poke.name, abilityName))
        elif action == ActionType.CLEAR_BOOST:
            #[]|-clearboost|p1a: Marshadow
            teamID, pokeName = self.strip_team(params[2])
            poke = self.get_pokemon(None, pokeName, teamID=teamID)

            print("%s had its stats reset" % poke.name)
            poke.statMultipliers = copy.deepcopy(poke.baseMultipliers)
        elif action == ActionType.CRIT:
            print("CRIT")
            print(params)
        elif action == ActionType.START:
            # Example: []|-start|p2a: Zekrom|confusion|[fatigue]
            teamID, pokeName = self.strip_team(params[2])
            startEvent = params[3]

            if startEvent == "confusion":
                self.get_pokemon(None, pokeName, teamID=teamID).set_status("confusion")
            elif startEvent == "Substitute":
                if teamID == self.id:
                    print("Sub started for my team")
                    self.teamHasSub = True
                else:
                    print("Sub started for enemy")
                    self.enemyHasSub = True
            else:
                print("%s started with %s" % (pokeName, startEvent))
        elif action == ActionType.END:
            # Example: []|-end|p2a: Zekrom|confusion
            teamID, pokeName = self.strip_team(params[2])
            endEvent = params[3]

            if endEvent == "confusion":
                self.get_pokemon(None, pokeName, teamID=teamID).remove_status("confusion")
            elif endEvent == "Substitute":
                if teamID == self.id:
                    print("Sub ended for my team")
                    self.teamHasSub = False
                else:
                    print("Sub ended for enemy")
                    self.enemyHasSub = False
            else:
                print("%s ended with %s" % (pokeName, endEvent))

    def handle_details_changed(self, params):
        # Example: []|detailschange|p1a: Zygarde|Zygarde-Complete, L73
        teamID, pokeName = self.strip_team(params[2])
        newPokeName = string_parse(params[3].split(",")[0])
        poke = self.get_pokemon(None, pokeName, teamID=teamID)

        poke.parse_pokemon_info(params[2], params[3])

        if teamID == self.id:
            pokeDict = ast.literal_eval(self.teamJSON)["side"]["pokemon"][newPokeName]
            poke.stats = pokeDict["stats"]
            poke.possible_abilities = [pokeDict["baseAbility"]]

        print("Transformed into %s" % newPokeName)

    def set_health(self, pokeStr, healthStr):
        teamID, pokeName = self.strip_team(pokeStr)
        health = int(healthStr.split("/")[0])

        poke = None
        if teamID == self.id:
            poke = self.get_pokemon(self.team, pokeName)
        else:
            poke = self.get_pokemon(self.enemyTeam, pokeName)
        
        poke.set_health(health)

    def get_pokemon(self, team, pokeName, teamID=""):
        """Returns pokemon object from a list

        Returns the pokemon if found, none otherwise
        """

        if teamID != "":
            if teamID == self.id:
                team = self.team
            else:
                team = self.enemyTeam

        for poke in team:
            if poke.name in pokeName:
                return poke
        return None


    def parse_round(self, validTurnData):
        """Processes the console information on the match

        Handles extracting the parameters out of the console log and calling
        a handler to handle the event occuring
        """
        mainAction = None

        for turnData in validTurnData:
            for line in turnData.split("\\n"):
                actionTuple = get_action_type(line)

                if actionTuple == None:
                    continue
                
                aType, action = actionTuple
                params = line.split("|")

                for param in params:
                    if "[from]" in param:
                        self.handle_from(params)
                        break

                if aType == ActionType.MAIN:
                    mainAction = action
                    self.handle_main_action(action, params)
                elif aType == ActionType.SUB:
                    self.handle_sub_action(mainAction, action, params)
                else:
                    print("ERROR ACTION NOT HANDLED")
        return self

    def strip_team(self, pokeString):
        """Extracts a team and pokemon name from a string

        Inputs:
        pokeString - String in the format of "pxa: pokemonName"

        Returns:
        tuple of the team ID and pokemon strings
        """
        teamID, pokeName = pokeString.split(": ")
        teamID = teamID.replace("a", "")

        pokeName = string_parse(pokeName)

        return (teamID, pokeName)
    
    def handle_from(self, params):
        #[]|-enditem|p2a: Dialga|Leftovers|[from] move: Knock Off|[of] p1a: Landorus
        #[]|-damage|p1a: Landorus|33/250|[from] item: Life Orb
        
        print("FROM")
        print(params)

        details = None
        item = None
        for param in params:
            if "p1" in param or "p2" in param and details is None:
                details = param
            if "[from] item:" in param:
                item = param.split("item: ")[1]
                item = string_parse(item)
        
        if item is None:
            print(params)
            return

        teamID, pokeName = self.strip_team(details)
        self.get_pokemon(None, pokeName, teamID=teamID).set_item(item)

        



    def handle_move(self, params):
        """Handles the move event

        This will decrease the pp used for a move and note the move if it hasnt
        seen it before.
        """
        # Example
        #[]|move|p1a: Espeon|Toxic|p2a: Quagsire|[from]Magic Bounce

        # Set actionParams for sub events
        self.actionParams = params

        if len(params) >= 6:
            fromStr = params[5]
            if "Magic Bounce" in fromStr:
                print("Magic Bounce handled")
                return

        # Get team id and pokemon name
        teamID, pokeName = self.strip_team(params[2])
        moveUsed = string_parse(params[3])

        poke = None
        # True if our team
        if teamID == self.id:
            # Get the pokemon from our team
            poke = self.get_pokemon(self.team, pokeName)
        else:
            # Get the pokemon from the enemy team
            poke = self.get_pokemon(self.enemyTeam, pokeName)
            # Check to see if its in their move list, otherwise add it
            if moveUsed not in poke.pokeMoveDict.keys():
                print("%s not seen before by this pokemon" % moveUsed)
                poke.add_move(moveUsed)
        
        if moveUsed == "struggle":
            print("TODO: Handle struggle")
            return

        # Decrease PP of move
        print("%s pp decreased" % moveUsed)
        poke.pokeMoveDict[moveUsed]["curr_pp"] -= 1

    
    def handle_sub_move(self, action, params):
        """Handles sub-events relating to the main event MOVE
        """

        if action == ActionType.DAMAGE:
            damagedPokemon = params[2]
            teamID, pokeName = self.strip_team(damagedPokemon)

            health = params[3]
            health = int(health.split("/")[0])

            poke = None
            if teamID == self.id:
                poke = self.get_pokemon(self.team, pokeName)
            else:
                poke = self.get_pokemon(self.enemyTeam, pokeName)
            poke.set_health(health)


    def handle_switch(self, params):
        """Handles the main event SWITCH

        Checks to see what team switched, if ours we set the pokemon to active.
        Otherwise checks to see if enemy pokemon was seen before, if not, add
        it to its memory
        """
        print(params)
        teamID, pokeName = self.strip_team(params[2])

        # True if our team
        if teamID == self.id:
            self.teamHasSub = False
            # Iterate over pokemon setting its active status to True/False
            for poke in self.team:
                print("%s had its stats reset" % poke.name)
                poke.statMultipliers = copy.deepcopy(poke.baseMultipliers)
                poke.isActive = poke.name in pokeName
                if poke.name in pokeName:
                    print("%s on your team is now set to active" % poke.name)
            return
        
        # Otherwise its the enemy team
        # Boolean to store if pokemon exists
        foundPokemon = False
        self.enemyHasSub = False
        for poke in self.enemyTeam:
            print("%s had its stats reset" % poke.name)
            poke.statMultipliers = copy.deepcopy(poke.baseMultipliers)
            # If pokemon found, set foundPokemon to true
            # Also set teams active status to True/False
            if poke.name in pokeName:
                print("%s on enemy team set to active" % poke.name)
                poke.isActive = True
                foundPokemon = True
            else:
                poke.isActive = False
        

        if foundPokemon:
            return

        # Create new pokemon object
        poke = Pokemon(None, self.nameDict, self.itemDict, self.abilDict, self.moveDict)

        # Give info on its name, level, and gender
        poke.parse_pokemon_info(params[2], params[3])
        poke.maxHP = poke.currHP = 100.0  # Enemy health is only known in percents
        poke.isActive = True  # Set to the active field pokemon

        print("%s created for enemy team" % poke.name)

        self.enemyTeam.append(poke)


    def print_info(self):
        print("-----------------------")
        print("Field: %s" % self.field)
        print("Weather: %s" % self.weather)
        print("-----------------------")
        print("My Pokemon:")
        for poke in self.team:
            poke.print_details()
            print()
        print("-----------------------")
        print("My Hazards: ", end='')
        if self.teamHasSub:
            print("Subsitute active")
        print(self.hazards)
        print("-----------------------")
        print("Enemy Pokemon:")
        for poke in self.enemyTeam:
            poke.print_details()
            print()
        print("-----------------------")
        print("Enemy Hazards: ", end='')
        if self.enemyHasSub:
            print("Enemy subsitute active")
        print(self.enemyHazards)

