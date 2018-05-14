from Pokemon import Pokemon
import copy

class GameState:
    def __init__(self):
        self.teams = [[None]*6, [None]*6]
        self.biasTeams = [[None]*6, [None]*6]

    def setTeam(self, teamIdx, team):
        self.teams[teamIdx] = team
