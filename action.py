import logging
import numpy as np

from showdown.data import all_move_json, pokedex
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
    START           = 35

action_map = {
    "move"          : ActionType.MOVE,
    "switch"        : ActionType.SWITCH,
    "detailschange" : ActionType.DETAILS_CHANGED,
    "-formechange"  : ActionType.FORM_CHANGED,
    "replace"       : ActionType.REPLACE,
    "swap"          : ActionType.SWAP,
    "cant"          : ActionType.CANT,
    "faint"         : ActionType.FAINT,
    "-fail"         : ActionType.FAIL,
    "-damage"       : ActionType.DAMAGE,
    "-heal"         : ActionType.HEAL,
    "-status"       : ActionType.STATUS,
    "-curestatus"   : ActionType.CURE_STATUS,
    "-cureteam"     : ActionType.CURE_TEAM,
    "-boost"        : ActionType.BOOST,
    "-unboost"      : ActionType.UNBOOST,
    "-weather"      : ActionType.WEATHER,
    "-fieldstart"   : ActionType.FIELD_START,
    "-fieldend"     : ActionType.FIELD_END,
    "-sidestart"    : ActionType.SIDE_START,
    "-sideend"      : ActionType.SIDE_END,
    "-crit"         : ActionType.CRIT,
    "-item"         : ActionType.ITEM,
    "-enditem"      : ActionType.END_ITEM,
    "-ability"      : ActionType.ABILITY,
    "-endability"   : ActionType.END_ABILITY,
    "-transform"    : ActionType.TRANSFORM,
    "-activate"     : ActionType.ACTIVATE,
    "drag"          : ActionType.DRAG,
    "-end"          : ActionType.END,
    "-immune"       : ActionType.IMMUNE,
    "turn"          : ActionType.NEW_TURN,
    "-clearboost"   : ActionType.CLEAR_BOOST,
    "-start"        : ActionType.START,
}

max_params = 14
param_lengths = [10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10]


move_count = 0
for move_key in all_move_json:
    all_move_json[move_key]['move_index'] = move_count
    move_count += 1

poke_count = 0
for poke_key in pokedex:
    pokedex[poke_key]['poke_index'] = poke_count
    poke_count += 1

class Action:

    action_type = None
    params = None
    encoding = None

    @classmethod
    def createAction(cls, msg):
        if not cls.is_valid_message(msg):
            return None

        self = Action()
        self.params = msg.split("|")[1:]
        self.action_type = action_map[self.params[0]]

        logging.info("Mapping %s -> %s with %d parameters"
            % (self.params[0], self.action_type, len(self.params)-1))

        self.encode()

        return self
    
    @classmethod
    def is_valid_message(cls, msg):
        key = msg.split("|")
        if len(key) == 1:
            return False
        
        key = key[1]

        if key in action_map:
            return True
        else:
            logging.debug("Can't map '%s' to an action" % msg)
            return False
    
    def get_action_embedding(self):
        action_one_hot = np.zeros(len(action_map))
        action_one_hot[self.action_type] = 1

        return action_one_hot

    def get_move_embedding(self, moveStr):
        move_one_hot = np.zeros(len(all_move_json))
        move_index = all_move_json[moveStr]['move_index']
        move_one_hot[move_index] = 1

        return move_one_hot

    
    def get_poke_embedding(self, pokeStr):
        poke_one_hot = np.zeros(len(pokedex))
        poke_index = pokedex[pokeStr]['poke_index']
        poke_one_hot[poke_index] = 1

        return poke_one_hot

    def handle_move_encoding(self):
        player1_one_hot, poke1_one_hot = self.handle_pokemon_encoding(self.params[1])

        move_str = self.strip_key(self.params[2])
        move_one_hot = self.get_move_embedding(move_str)

        if ":" not in self.params[3]:
            player2_one_hot = player1_one_hot.copy()
            poke2_one_hot = poke1_one_hot.copy()
        else: 
            player2_one_hot, poke2_one_hot = self.handle_pokemon_encoding(self.params[3])

        logging.debug("Finished MOVE encoding")


    def handle_damage_encoding(self):
        player_one_hot, poke_one_hot = self.handle_pokemon_encoding(self.params[1])

        damage_str = self.params[2]
        damage_percent = 0.0
        if "/" in damage_str:
            curr_health, max_health = damage_str.split("/")

            if ' ' in max_health:
                max_health = max_health.split(' ')[0]

            curr_health = float(curr_health)
            max_health = float(max_health)

            damage_percent = curr_health / max_health

    
    def handle_pokemon_encoding(self, pokemon_str):
        player_str, poke_name = pokemon_str.split(": ")
        poke_name = self.strip_key(poke_name)

        # TODO Need to change this to be if this is us or not
        player_one_hot = np.zeros(2)
        if player_str == "p1a":
            player_one_hot[0] = 1
        else:
            player_one_hot[1] = 0

        poke_one_hot = self.get_poke_embedding(poke_name)

        return (player_one_hot, poke_one_hot)

        

    def strip_key(self, key):
        remove_list = [' ', '-', '\'']
        key = key.lower()

        for item in remove_list:
            key = key.replace(item, '')

        return key

    
    def encode(self):
        # TODO: There's some actions we dont care to encode
        action_one_hot = np.zeros(35)
        action_one_hot[self.action_type.value] = 1

        encoders = {
            ActionType.MOVE : self.handle_move_encoding,
            ActionType.DAMAGE : self.handle_damage_encoding,
        }

        encoder = encoders.get(self.action_type, None)

        if encoder:
            #try:
            encoder()
            #except:
            #    print("%s failed to encode." % self.action_type)
            #    print(self.params)
        else:
            pass
            #print("%s not yet handled" % self.action_type)
