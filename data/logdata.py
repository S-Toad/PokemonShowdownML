
from enum import Enum

class ActionType(Enum):
    MOVE            =  0
    SWITCH          =  1
    DETAILS_CHANGED =  2
    FORM_CHANGED    =  3
    REPLACE         =  4
    SWAP            =  5
    CANT            =  6
    FAINT           =  7
    FAIL            =  8
    DAMAGE          =  9
    HEAL            = 10
    STATUS          = 11
    CURE_STATUS     = 12
    CURE_TEAM       = 13
    BOOST           = 14
    UNBOOST         = 15
    WEATHER         = 16
    FIELD_START     = 17
    FIELD_END       = 18
    SIDE_START      = 19
    SIDE_END        = 20
    CRIT            = 21
    ITEM            = 22
    END_ITEM        = 23
    ABILITY         = 24
    END_ABILITY     = 25
    TRANSFORM       = 26
    ACTIVATE        = 27
    DRAG            = 28
    END             = 29
    IMMUNE          = 30
    NEW_TURN        = 31
    MAIN            = 32
    SUB             = 33
    CLEAR_BOOST     = 34

logActionDict = {
    "|move|"          : ActionType.MOVE,
    "|switch|"        : ActionType.SWITCH,
    "|detailschange|" : ActionType.DETAILS_CHANGED,
    "|-formechange|"  : ActionType.FORM_CHANGED,
    "|replace|"       : ActionType.REPLACE,
    "|swap|"          : ActionType.SWAP,
    "|cant|"          : ActionType.CANT,
    "|faint|"         : ActionType.FAINT,
    "|-fail|"         : ActionType.FAIL,
    "|-damage|"       : ActionType.DAMAGE,
    "|-heal|"         : ActionType.HEAL,
    "|-status|"       : ActionType.STATUS,
    "|-curestatus|"   : ActionType.CURE_STATUS,
    "|-cureteam|"     : ActionType.CURE_TEAM,
    "|-boost|"        : ActionType.BOOST,
    "|-unboost|"      : ActionType.UNBOOST,
    "|-weather|"      : ActionType.WEATHER,
    "|-fieldstart|"   : ActionType.FIELD_START,
    "|-fieldend|"     : ActionType.FIELD_END,
    "|-sidestart|"    : ActionType.SIDE_START,
    "|-sideend|"      : ActionType.SIDE_END,
    "|-crit|"         : ActionType.CRIT,
    "|-item|"         : ActionType.ITEM,
    "|-enditem|"      : ActionType.END_ITEM,
    "|-ability|"      : ActionType.ABILITY,
    "|-endability|"   : ActionType.END_ABILITY,
    "|-transform|"    : ActionType.TRANSFORM,
    "|-activate|"     : ActionType.ACTIVATE,
    "|drag|"          : ActionType.DRAG,
    "|-end|"          : ActionType.END,
    "|-immune|"       : ActionType.IMMUNE,
    "|turn|"          : ActionType.NEW_TURN,
    "|-clearboost|"   : ActionType.CLEAR_BOOST
}

def get_action_type(logLine, printDetails=False):
    for key in logActionDict.keys():
        if key in logLine:
            if printDetails:
                try:
                    print_details(logActionDict[key], logLine)
                except:
                    print(logLine.split("|"))
            
            if "|-" in key:
                return (ActionType.SUB, logActionDict[key])
            else:
                return (ActionType.MAIN, logActionDict[key])


    return None

def is_valid_log(logString):
    for actionID in logActionDict.keys():
        if actionID in logString:
            return True
    return False


def print_details(action, logLine):
    logList = logLine.split("|")

    oneParam = None
    twoParam = None
    threeParam = None

    #print(logList)

    if len(logList) >= 3:
        oneParam = logList[2]
    
    if len(logList) >= 4:
        twoParam = tuple(logList[2:4])
    
    if len(logList) >= 5:
        threeParam = tuple(logList[2:5])

    if action ==  ActionType.ABILITY:
        print("%s used %s" % twoParam)
    elif action ==  ActionType.ACTIVATE:
        print("%s was activated" % oneParam)
        print(logList)
    elif action ==  ActionType.BOOST:
        print("%s increased %s by %s" % threeParam)
    elif action ==  ActionType.CANT:
        print("%s cant due to %s" % twoParam)
        print(logList)
    elif action ==  ActionType.CRIT:
        print("%s crit" % oneParam)
    elif action ==  ActionType.CURE_STATUS:
        print("%s was cured of %s" % twoParam)
    elif action ==  ActionType.CURE_TEAM:
        print("%s cured team" % oneParam)
    elif action ==  ActionType.DAMAGE:
        if threeParam != None:
            print("%s damaged, now at %s from %s" % threeParam)
        else:
            print("Prev action caused %s to be at %s" % twoParam)
    elif action ==  ActionType.DETAILS_CHANGED:
        print("%s now %s at %s" % threeParam)
    elif action ==  ActionType.DRAG:
        print("%s switched with %s due to %s" % threeParam)
    elif action ==  ActionType.END_ABILITY:
        print("%s ability ended" % oneParam)
    elif action ==  ActionType.END_ITEM:
        print("%s ended using %s" % twoParam)
    elif action ==  ActionType.FAIL:
        print("Last action failed")
    elif action ==  ActionType.FAINT:
        print("%s fainted" % oneParam)
    elif action ==  ActionType.FIELD_END:
        print("%s ended" % oneParam)
    elif action ==  ActionType.FIELD_START:
        print("%s started" % oneParam)
    elif action ==  ActionType.FORM_CHANGED:
        print("%s changed to %s at %s" % threeParam)
    elif action ==  ActionType.HEAL:
        print("%s healed to %s from %s" % threeParam)
    elif action ==  ActionType.ITEM:
        print("%s used %s" % twoParam)
    elif action ==  ActionType.MOVE:
        print("%s used %s at %s" % threeParam)
    elif action ==  ActionType.REPLACE:
        print("%s replaced %s with %s" % threeParam)
    elif action ==  ActionType.SIDE_END:
        print("%s ended %s" % twoParam)
    elif action ==  ActionType.SIDE_START:
        print("%s started %s" % twoParam)
    elif action ==  ActionType.STATUS:
        print("%s inflicted with %s" % twoParam)
    elif action ==  ActionType.SWAP:
        print("%s swapped with %s" % twoParam)
    elif action ==  ActionType.SWITCH:
        print("%s switched with %s at %s" % threeParam)
    elif action ==  ActionType.TRANSFORM:
        print("%s transformed to %s" % twoParam)
    elif action ==  ActionType.UNBOOST:
        print("%s %s was lowered by %s" % threeParam)
    elif action ==  ActionType.WEATHER:
        print("%s started" % oneParam)
    elif action == ActionType.END:
        print("%s %s" % twoParam)
    elif action == ActionType.IMMUNE:
        print("%s %s" % twoParam)
    else:
        print("%s not logged yet!" % action)
    print(action)
