import asyncio
import json
import random

from asyncio import TimeoutError
from enum import Enum
import logging
from state.action import Action, ActionType
from state.team import PokemonTeam
from threading import Thread

class BattleState(Enum):
    ANY_ACTION = 0
    NEED_SWITCH = 1     # Occurs when pokemon is fainted or forced out
    NEED_MOVE = 2       # Occurs when a pokemon is locked in
    WIN = 4
    LOSS = 5
    WAITING = 6
    STARTING_GAME = 7
    WAITING_FOR_UPDATES = 8

class ChoiceType(Enum):
    MOVE = 0
    SWITCH = 1


class BattleClient:
    current_battle_state = None
    action_sequence = None
    battle_logger = None
    
    listen = False
    listen_thread = None
    
    websocket = None
    rqid = None
    battle_id = None

    player_side = None
    username = None
    enemy = None

    team = None
    turn_number = None

    @property
    def url(self):
        return "https://play.pokemonshowdown.com/%s" % self.battle_id

    def __init__(self, websocket, battle_log=None):
        self.websocket = websocket
        self.action_sequence = []
        self.current_battle_state = BattleState.STARTING_GAME
        self.turn_number = 0

        if battle_log:
            formatter = logging.Formatter("%(levelname)s : %(message)s")
            fileHandler = logging.FileHandler(battle_log + '.log', mode='w')
            fileHandler.setFormatter(formatter)
            self.battle_logger = logging.getLogger(battle_log)
            self.battle_logger.addHandler(fileHandler)
    
    def __eq__(self, obj):
        if isinstance(obj, BattleClient):
            return obj.current_battle_state == self.current_battle_state
        else:
            return obj == self.current_battle_state
    
    def __ne__(self, obj):
        return not self.__eq__(obj)

    def log(self, level, msg, *args):
        msg = "Turn %d : %s" % (self.turn_number, msg)

        if self.battle_logger:
            self.battle_logger.log(level, msg, *args)
    
    def set_battle_state(self, new_battle_state):
        self.current_battle_state = new_battle_state
        self.log(logging.DEBUG, "Battle state is now %s", new_battle_state)
    
    async def make_choice(self, choice_type, choice_val):
        self.log(logging.INFO, "Chose %s:%s with rqid=%s", choice_type, choice_val, self.rqid)

        if choice_type == ChoiceType.MOVE:
            msg = "%s|/choose move %d|%d" % (self.battle_id, choice_val, self.rqid)
        elif choice_type == ChoiceType.SWITCH:
            msg = "%s|/choose switch %d|%d" % (self.battle_id, choice_val, self.rqid)
        else: pass  # Left in for future cases
        
        await self.websocket.send(msg)
    
    async def perform_random_action(self):
        r = random.randint(1, 10)
        switch_threshold = 8

        if r < switch_threshold or not self.team.switch_available():
            await self.perform_random_move()
        else:
            await self.perform_random_switch()
    
    async def wait_for_updates(self):
        # TODO: I think this can be replaced by a blocking call
        # to listen_for_actions where it'll break once our terminating
        # condition was found
        self.set_battle_state(BattleState.WAITING_FOR_UPDATES)
        self.log(logging.DEBUG, "Starting to wait for updates")

        await self.start_listen_for_actions()
        while self != BattleState.ANY_ACTION \
                and self != BattleState.NEED_MOVE \
                and self != BattleState.NEED_SWITCH \
                and self != BattleState.WAITING \
                and (self == BattleState.STARTING_GAME \
                    or self == BattleState.WAITING_FOR_UPDATES):
            await asyncio.sleep(0)
        await self.stop_listen_for_actions()

        self.log(logging.DEBUG, "Stopped listening to updates because: %s",
            self.current_battle_state)

    async def perform_random_move(self):
        decision = ChoiceType.MOVE
        options = [1, 2, 3, 4]
        random.shuffle(options)

        made_move = False
        for option_val in options:
            if self.team.is_move_allowed(option_val):
                await self.make_choice(decision, option_val)
                made_move = True
                break
        
        if not made_move:
            self.log(logging.INFO, "Couldn't make a move!")


    async def perform_random_switch(self, update=False):
        decision = ChoiceType.SWITCH
        options = [1, 2, 3, 4, 5, 6]
        random.shuffle(options)

        made_switch = False
        for option_val in options:
            choice_index = self.team.get_poke_choice_index_if_valid(option_val)
            if choice_index:
                await self.make_choice(decision, choice_index)
                made_switch = True
                break
        
        if not made_switch:
            self.log(logging.INFO, "Couldn't make a switch!")
        
        if update:
            await self.wait_for_updates()

    async def start_listen_for_actions(self):
        self.listen = True
        self.listen_task = asyncio.create_task(self.listen_for_actions())
    
    async def stop_listen_for_actions(self):
        self.listen = False
        await self.listen_task

    async def listen_for_actions(self):
        while self.listen:
            msg = await self.receive_msg(timeout=0.05)

            if msg:
                for line in msg.splitlines():
                    self.log(logging.DEBUG, "Received: %s", line)
                    if self.battle_id is None and ">battle-gen7" in line:
                        self.battle_id = line[1:]
                    else:
                        self.handle_action_msg(line)
    
    def handle_action_msg(self, line):
        action = Action.createAction(line)

        if action is None: return
        
        self.log(logging.DEBUG, "Found a %s action", action)
        
        if action == ActionType.REQUEST:
            self.handle_request_action(action)
        elif action == ActionType.NEW_TURN:
            self.turn_number += 1
            self.set_battle_state(BattleState.ANY_ACTION)
        elif action == ActionType.WIN:
            self.set_battle_state(BattleState.WIN)
        elif action == ActionType.LOSS:
            self.set_battle_state(BattleState.LOSS)
        elif action ==  ActionType.ERROR:
            self.handle_error_action(action)
        #elif action == ActionType.FAINT:
        #    self.set_battle_state(BattleState.NEED_SWITCH)
        else:
            self.action_sequence.append(action)
    
    def handle_request_action(self, request_action):
        json_str = request_action.params[1]
        self.log(logging.DEBUG, "Request JSON received: %s", json_str)
        if json_str != '':

            request_dict = json.loads(json_str)
            self.rqid = request_dict['rqid']

            if 'forceSwitch' in request_dict and request_dict['forceSwitch'][0]:
                self.set_battle_state(BattleState.NEED_SWITCH)
            elif 'wait' in request_dict and request_dict['wait']:
                self.set_battle_state(BattleState.WAITING)
            if self.team is None:
                self.log(logging.INFO, "Constructing team")
                self.team = PokemonTeam(request_dict)
                self.player_side = request_dict['side']['id']
            else:
                self.log(logging.INFO, "Starting update of team")
                self.team.update_from_dict(request_dict)
                self.log(logging.INFO, "Done updating team")

            self.log(logging.DEBUG, "Done handling request")
    
    def handle_error_action(self, action):
        self.log(logging.DEBUG, "Found error: %s", action.params)
    
    async def receive_msg(self, timeout=1):
        try:
            msg = await asyncio.wait_for(self.websocket.recv(), timeout=timeout)
            # Any other message stripping can occur here
            msg = msg.replace('\u2606', '')
            return msg
        except TimeoutError: return None
    
    def get_available_switches(self):
        pass

    def get_available_moves(self):
        pass