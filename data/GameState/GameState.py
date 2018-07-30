from .Pokemon import Pokemon
from enum import Enum
import copy

class GameState():
    def __init__(self):
        self.nextState = None
        self.prevState = None

        self.p1Team = [None] * 6
        self.p2Team = [None] * 6

        self.p1Action = None
        self.p2Action = None

    def next_state(self):
        gs = GameState()
        gs.prevState = self
        gs.p1Team = self.p1Team
        self.p2Team = self.p2Team

        return gs

    def parse_round(self, roundLog):
        print("------------------------------")
        print(roundLog)
        print("------------------------------")
        """
        actions = roundLog.split("\n")

        for action in actions:
            if "|move|" in action:
                self.handle_move(action)
            elif "|switch|" in action:
                self.handle_switch(action)
            else:
                print("Unknown: " + action)
        """
    
    def handle_move(self, actionLog):
        details = actionLog.split("|")
        pokeDetail = details[1]
        moveDetail = details[2]
        targetDetail = details[3]

        print(pokeDetail)
        print(moveDetail)
        print(targetDetail)
    
    def handle_switch(self, actionLog):
        details = actionLog.split("|")
        pokeDetail = details[1]
        info = details[2]
        hpDetail = details[3]

        print(pokeDetail)
        print(info)
        print(hpDetail)

class ActionType(Enum):
    SWITCH  = 0
    ATTACK  = 1
    NOTHING = 2

class Action:
    def __init__(self, actionType):
        self.actionType = actionType
