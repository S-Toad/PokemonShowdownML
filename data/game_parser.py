
from GameState.GameState import GameState, Pokemon
import json

def game_parser(filePath):
    turns = breakLog(filePath)
    teams = getTeams(filePath)
    
    #gameStates = [GameState(0), GameState(1), GameState(2)]
    for turn in turns:
        parseTurn(turn)
        #gameStates = (parseTurn(turn, gameStates))

def getTeams(filePath):
    content = None
    with open(filePath) as f:
        content = f.readlines()
    
    teamStrs = [content[-2], content[-1]]
    teams = [[],[]]
    for i in range(0,2):
        pokeStrs = teamStrs[i].strip().split(":")
        for j in range(0,6):
            poke = Pokemon()
            infoList = pokeStrs[j].split(",")

            poke.ID = infoList[0]
            poke.itemID = infoList[1]
            poke.abilityID = infoList[2]
            poke.types.append(infoList[3])
            if infoList[4] != -1:
                poke.types.append(infoList[4])
            poke.moves = infoList[5].split("|")

            teams[i].append(poke)
    return teams


def parseTurn(turn):
    turn.pop(0)
    for action in turn:
        action = action.strip()
        if boringAction(action):
            #print("Boring Action Deemed: " + action)
            continue
        print('"' + action + '"')
    print("--------------------")
        

    return None

def boringAction(action):
    return ("|turn|" in action
        or "|inactive|" in action
        or "|" == action
        or "|-supereffective|" in action
        or "|-resisted|" in action
        or "|upkeep" == action
        or "|faint|" in action
        or "|-crit|" in action
        or "|-message|" in action
    )

def breakLog(filePath):
    content = None
    with open(filePath) as f:
        content = f.readlines()
    if content is None:
        return
    
    turns = []
    startIndex = None
    for index, line in enumerate(content):
        if "|turn|" not in line:
            continue
        if startIndex is None:
            startIndex = index
            continue
        print("Start:End = " + str(startIndex) + ":" + str(index))
        turns.append(content[startIndex:index])
        startIndex = index
    return turns
