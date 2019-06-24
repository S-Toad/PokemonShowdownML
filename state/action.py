import logging
import numpy as np
import traceback

from state.data import ability_dict, pokedex_dict, move_dict, item_dict, \
    stat_dict, status_dict, weather_dict, side_dict, start_dict, activate_dict
from state.action_type import ActionType, action_map

ABILITY_ENCODING_LENGTH = 9
POKE_ENCODING_LENGTH = 10
MOVE_ENCODING_LENGTH = 12
STAT_COUNT = len(stat_dict)
STATUS_COUNT = len(status_dict)
WEATHER_COUNT = len(weather_dict)
SIDE_COUNT = len(side_dict)
START_COUNT = len(start_dict)
ACTIVATE_COUNT = len(activate_dict)
class Action:
    action_type = None
    params = None
    encoding = None
    logger = None

    # createAction is our factory, however we may make
    # actions outside of this for logic sake
    def __init__(self, action_type=None):
        self.action_type = action_type

    @classmethod
    def createAction(cls, msg, logger=None):
        if not cls.is_valid_message(msg):
            return None

        self = Action()
        self.params = msg.split("|")[1:]
        self.action_type = action_map[self.params[0]]
        self.logger = logger

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
            #logging.debug("Can't map '%s' to an action" % msg)
            return False
    
    def __eq__(self, obj):
        if isinstance(obj, Action):
            return obj.action_type == self.action_type
        else:
            return obj == self.action_type
    
    def __ne__(self, obj):
        return not self.__eq__(obj)
    
    def __str__(self):
        return str(self.action_type)
    
    def log(self, level, msg, *args):
        if self.logger:
            msg = "%s : %s" % (str(self), msg)
            self.logger.log(level, msg, *args)
    
    def strip_key(self, orig_key):
        remove_list = [' ', '-', '\'']
        key = orig_key.lower()

        for item in remove_list:
            key = key.replace(item, '')

        self.log(logging.DEBUG, '%s ---> %s', orig_key, key)

        return key
    
    def get_action_embedding(self):
        action_one_hot = np.zeros(len(action_map), dtype=int)
        action_one_hot[self.action_type] = 1

        return action_one_hot

    def to_binary_encoding(self, value, binary_length):
        binary_encoding = np.zeros(binary_length, dtype=int)
        value_binary_str = "{0:b}".format(value)

        i = binary_length - len(value_binary_str)
        for c in value_binary_str:
            binary_encoding[i] = int(c)
            i += 1
        
        return binary_encoding

    def get_move_binary_encoding(self, move_str):
        move_index = move_dict[move_str]['index']
        return self.to_binary_encoding(move_index, MOVE_ENCODING_LENGTH)

    def get_team_encoding(self, poke_team_str, team_str):
        team_encoding = np.zeros(1, dtype=int)
        if team_str in poke_team_str:
            self.log(logging.DEBUG, "Identified team as ours")
            team_encoding[0] = 1
        else:
            self.log(logging.DEBUG, "Identified team as opponents")
        
        return team_encoding
    
    def get_poke_encoding(self, poke_str, team_str):
        if poke_str == '' or poke_str == 'null':
            self.log(logging.DEBUG, "Returning all zeros for %s", poke_str)
            return np.zeros(POKE_ENCODING_LENGTH, dtype=int)

        poke_team_str, poke_name_str = poke_str.split(": ")
        poke_name_str = self.strip_key(poke_name_str)

        team_encoding = self.get_team_encoding(poke_team_str, team_str)

        poke_index = pokedex_dict[poke_name_str]['index']
        poke_encoding = self.to_binary_encoding(poke_index, POKE_ENCODING_LENGTH)

        self.log(logging.DEBUG, "Index received was %d, interpreted as %s",
            poke_index, poke_encoding)

        return np.append(team_encoding, poke_encoding)

    def handle_move_encoding(self, team_str):
        poke1_str = self.params[1]
        poke2_str = self.params[3]
        move_str = self.strip_key(self.params[2])

        self.log(logging.DEBUG, "poke1='%s', poke2='%s', move='%s'",
            poke1_str, poke2_str, move_str)

        poke1_encoding = self.get_poke_encoding(poke1_str, team_str)
        poke2_encoding = self.get_poke_encoding(poke2_str, team_str)
        move_encoding = self.get_move_binary_encoding(move_str)

        encoding = np.append(poke1_encoding, poke2_encoding)
        encoding = np.append(encoding, move_encoding)

        return encoding

    def handle_simple_encoding(self, team_str):
        poke_str = self.params[1]
        return self.get_poke_encoding(poke_str, team_str)

    def handle_damage_encoding(self, team_str):
        # TODO: Sometimes healing/damage can be from items or abilities
        # We need to register these as separate events somehow
        # TODO: If healing/damage does the same thing, feels like they
        # should be considered as a "HEALTH_CHANGE" event instead?
        poke_str = self.params[1]
        damage_str = self.params[2]

        poke_encoding = self.get_poke_encoding(poke_str, team_str)

        damage_percent = 0.0
        if "/" in damage_str:
            curr_health, max_health = damage_str.split("/")

            # Gets rid of conditions
            if ' ' in max_health:
                max_health = max_health.split(' ')[0]

            curr_health = float(curr_health)
            max_health = float(max_health)

            damage_percent = curr_health / max_health
            self.log(logging.DEBUG, "Setting health to %0.5f", damage_percent)
        else:
            self.log(logging.DEBUG, "Pokemon fainted")
        
        return np.append(poke_encoding, damage_percent)
    
    def handle_switch_encoding(self, team_str):
        poke_str = self.params[1]
        return self.get_poke_encoding(poke_str, team_str)
    
    def handle_ability_encoding(self, team_str):
        poke_str = self.params[1]
        poke_encoding = self.get_poke_encoding(poke_str, team_str)

        ability_str = self.params[2]
        ability_str = self.strip_key(ability_str)
        ability_index = ability_dict[ability_str]['index']
        ability_encoding = self.to_binary_encoding(ability_index, ABILITY_ENCODING_LENGTH)

        self.log(logging.DEBUG, "Received ability key='%s'", ability_str)
        self.log(logging.DEBUG, "Index received was %d, interpreted as %s",
            ability_index, ability_encoding)

        return np.append(poke_encoding, ability_encoding)
    
    def handle_boost_encoding(self, team_str):
        poke_str = self.params[1]
        stat_str = self.params[2]
        bonus_value = int(self.params[3])

        poke_encoding = self.get_poke_encoding(poke_str, team_str)
        
        stat_index = stat_dict[stat_str]['index']
        stat_encoding = np.zeros(STAT_COUNT)
        stat_encoding[stat_index-1] = 1
        self.log(logging.DEBUG, "Mapping stat=%s --> %s", stat_str, stat_encoding)

        boost_encoding = np.append(poke_encoding, stat_encoding)
        boost_encoding = np.append(boost_encoding, bonus_value)

        return boost_encoding

    def handle_unboost_encoding(self, team_str):
        return self.handle_boost_encoding(team_str)

    def handle_status_encoding(self, team_str):
        poke_str = self.params[1]
        status_str = self.params[2]

        poke_encoding = self.get_poke_encoding(poke_str, team_str)

        status_index = status_dict[status_str]['index']
        status_encoding = np.zeros(STATUS_COUNT)
        status_encoding[status_index-1] = 1

        self.log(logging.DEBUG, "Mapping status=%s --> %s", status_str, status_encoding)

        return np.append(poke_encoding, status_encoding)
    
    def handle_cure_status_encoding(self, team_str):
        return self.handle_status_encoding(team_str)
    
    def handle_fail_encoding(self, team_str):
        return self.handle_simple_encoding(team_str)
    
    def handle_immune_encoding(self, team_str):
        return self.handle_simple_encoding(team_str)
    
    def handle_crit_encoding(self, team_str):
        return self.handle_simple_encoding(team_str)
    
    def handle_resist_encoding(self, team_str):
        return self.handle_simple_encoding(team_str)
    
    def handle_heal_encoding(self, team_str):
        return self.handle_damage_encoding(team_str)
    
    def handle_weather_encoding(self, team_str):
        weather_str = self.params[1]
        weather_str = self.strip_key(weather_str)
        
        weather_encoding = np.zeros(WEATHER_COUNT)
        if weather_str == 'none':
            self.log(logging.DEBUG, "Weather was removed")
        else:
            weather_index = weather_dict[weather_str]['index']
            weather_encoding[weather_index-1] = 1
        
        self.log(logging.DEBUG, "Mapped %s ---> %s", weather_str, weather_encoding)
        
        upkeep = 0
        if len(self.params) == 3 and self.params[2] == '[upkeep]':
            self.log(logging.DEBUG, "Weather was upkeep")
            upkeep = 1
        
        return np.append(weather_encoding, upkeep)
    
    def handle_item_encoding(self, team_str):
        poke_str = self.params[1]
        item_str = self.params[2]

        poke_encoding = self.get_poke_encoding(poke_str, team_str)

        item_str = self.strip_key(item_str)
        item_index = item_dict[item_str]['index']
        item_encoding = np.zeros(item_dict['COUNT'])
        item_encoding[item_index-1] = 1

        self.log(logging.DEBUG, "Mapping %s ---> %s", item_index, item_encoding)

        return np.append(poke_encoding, item_encoding)
    
    def handle_end_item_encoding(self, team_str):
        return self.handle_item_encoding(team_str)
    
    def handle_side_start_encoding(self, team_str):
        side_str = self.params[1]
        effect_str = self.params[2]
    
        side_encoding = self.get_team_encoding(side_str, team_str)

        effect_str = effect_str.replace("move: ", "")
        effect_str = self.strip_key(effect_str)
        effect_index = side_dict[effect_str]['index']
        effect_encoding = np.zeros(SIDE_COUNT)
        effect_encoding[effect_index-1] = 1

        self.log(logging.DEBUG, 'Mapped %s ---> %s', effect_str, effect_encoding)
    
        return np.append(side_encoding, effect_encoding)

    def handle_side_end_encoding(self, team_str):
        return self.handle_side_start_encoding(team_str)
    
    def handle_cant_encoding(self, team_str):
        return self.handle_simple_encoding(team_str)
    
    def handle_start_encoding(self, team_str):
        poke_str = self.params[1]
        effect_str = self.params[2]

        poke_encoding = self.get_poke_encoding(poke_str, team_str)

        effect_str = effect_str.replace("move: ", "")
        effect_str = self.strip_key(effect_str)
        effect_index = start_dict[effect_str]['index']
        effect_encoding = np.zeros(START_COUNT)
        effect_encoding[effect_index-1] = 1

        return np.append(poke_encoding, effect_encoding)

    def handle_end_encoding(self, team_str):
        return self.handle_start_encoding(team_str)

    def handle_activate_encoding(self, team_str):
        poke_str = self.params[1]
        activate_str = self.params[2]

        poke_encoding = self.get_poke_encoding(poke_str, team_str)

        activate_str = activate_str.replace("ability: ", "")
        activate_encoding = np.zeros(ACTIVATE_COUNT)
        if activate_str not in activate_dict:
            self.log(logging.DEBUG, "%s was not used in activate", activate_str)
        else:
            activate_index = activate_dict[activate_str]['index']
            activate_encoding[activate_index-1] = 1
        
        return np.append(poke_encoding, activate_encoding)
    
    def handle_drag_encoding(self, team_str):
        return self.handle_switch_encoding(team_str)
    
    def handle_details_changed_encoding(self, team_str):
        return self.handle_simple_encoding(team_str)

    def encode(self, team_str):
        if self.encoding is not None:
            return
        
        if self == ActionType.FAINT or \
                self == ActionType.UPKEEP:
            self.log(logging.DEBUG, "%s does not need encoding.", self)
            self.encoding = []  # Used to supress logging in the future
            return

        encoders = {
            ActionType.MOVE            : self.handle_move_encoding,
            ActionType.DAMAGE          : self.handle_damage_encoding,
            ActionType.SWITCH          : self.handle_switch_encoding,
            ActionType.ABILITY         : self.handle_ability_encoding,
            ActionType.BOOST           : self.handle_boost_encoding,
            ActionType.UNBOOST         : self.handle_unboost_encoding,
            ActionType.STATUS          : self.handle_status_encoding,
            ActionType.IMMUNE          : self.handle_immune_encoding,
            ActionType.FAIL            : self.handle_fail_encoding,
            ActionType.CRIT            : self.handle_crit_encoding,
            ActionType.HEAL            : self.handle_heal_encoding,
            ActionType.WEATHER         : self.handle_weather_encoding,
            ActionType.CURE_STATUS     : self.handle_cure_status_encoding,
            ActionType.ITEM            : self.handle_item_encoding,
            ActionType.END_ITEM        : self.handle_end_item_encoding,
            ActionType.SIDE_START      : self.handle_side_start_encoding,
            ActionType.SIDE_END        : self.handle_side_end_encoding,
            ActionType.CANT            : self.handle_cant_encoding,
            ActionType.START           : self.handle_start_encoding,
            ActionType.END             : self.handle_end_encoding,
            ActionType.ACTIVATE        : self.handle_activate_encoding,
            ActionType.DRAG            : self.handle_drag_encoding,
            ActionType.DETAILS_CHANGED : self.handle_details_changed_encoding,
        }

        encoder = encoders.get(self.action_type, None)

        if encoder:
            self.log(logging.DEBUG, "Starting encoding...")
            self.log(logging.DEBUG, "Params=%s", self.params)

            try:
                action_one_hot = np.zeros(ActionType.PLACEHOLDER.value, dtype=int)
                action_one_hot[self.action_type.value] = 1

                self.log(logging.DEBUG, "action one-hot=%s", action_one_hot)

                action_encoding = encoder(team_str)
                self.encoding = np.append(action_one_hot, action_encoding)
                self.log(logging.DEBUG, "final encoding=%s", self.encoding)
                self.log(logging.DEBUG, "Done encoding!")
            except:
                print("%s failed to encode." % self.action_type)
                print(print(traceback.print_exc()))
                print(self.params)
                raise
        else:
            self.log(logging.DEBUG, "%s is not yet handled!", self)
            self.encoding = []  # Used to supress logging


    def is_terminating(self):
        return self.action_type == ActionType.NEW_TURN \
            or self.action_type == ActionType.WIN \
            or self.action_type == ActionType.TIE \
            or self.action_type == ActionType.ERROR
    
    def is_logic_action(self):
        return self.action_type.value >= ActionType.PLACEHOLDER.value
