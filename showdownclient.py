import asyncio
import json
import logging
import random
import re
import string
import time

from action import Action, ActionType
from enum import Enum
from queue import SimpleQueue
from showdown.websocket_communication import PSWebsocketClient

WEBSOCKET = "sim.smogon.com:8000"
RANDOM_BATTLE = "gen7randombattle"

# 2x1 vector on top
#   - <1,1> denotes any action is allowed
#   - <1,0> denotes a switch is needed
#   - <0,1> denotes a move is needed
class BattleState(Enum):
    ANY_ACTION = 0
    NEED_SWITCH = 1
    NEED_MOVE = 2
    DO_NOTHING = 3
    WIN = 4
    LOSS = 5
    WAITING = 6

class ChoiceType(Enum):
    MOVE = 0
    SWITCH = 1

class ShowdownClient:

    username = None
    ps_ws_client = None
    msg_queue = None
    current_battle_state = None
    action_sequence = None
    battle_id = None
    rqid = None
    last_request_json = None

    @classmethod
    async def createInstance(cls, username=None, password=None, websocket=WEBSOCKET):
        self = ShowdownClient()
        
        self.username = username
        if self.username is None:
            self.gen_username()

        logging.info("Spawning an instance for '%s'" % self.username)

        self.ps_ws_client = await PSWebsocketClient.create(
            self.username, password, websocket)
        
        return self
    
    @property
    def message_queue(self):
        return self.ps_ws_client.message_queue


    async def login(self):
        self.log("Logging in")
        await self.ps_ws_client.login()
    
    
    async def challenge_user(self, client=None, name=None,
            mode=RANDOM_BATTLE, team=''):
        
        if (client is not None and name is not None) \
                or (client is None and name is None):
            raise Exception("Client object xor name must be given.")
        
        if client is not None:
            name = client.username

        self.log("Attempting to challenge '%s'" % name)
        await self.ps_ws_client.challenge_user(name, mode, team)
    

    async def accept_challenge(self, mode=RANDOM_BATTLE, team=''):
        self.log("Attempting to accept challenge")
        await self.ps_ws_client.accept_challenge(mode, team)


    def log(self, msg, level=logging.INFO):
        msg = "%s : %s" % (self.username, msg)
        logging.log(level, msg)
    
    def is_battle_over(self):
        return self.current_battle_state == BattleState.WIN \
            or self.current_battle_state == BattleState.LOSS


    def gen_username(self, length=16):
        # Generates a string of some length using letters and digits
        characters = string.ascii_uppercase + string.digits
        self.username = ''.join(random.choices(characters, k=length))
    

    async def get_next_message(self, timeout=0.1):
        try:
            msg = await asyncio.wait_for(
                self.ps_ws_client.websocket.recv(), timeout=timeout)
            msg = msg.replace('\u2606', '')
            self.log("Received from websocket: {}".format(msg), logging.DEBUG)
            return msg
        except asyncio.TimeoutError:
            return None
    

    async def prepare_new_battle(self):
        self.action_sequence = []
        self.last_request_json = {}
        
        await self.get_turn_actions(timeout=60)

    async def make_choice(self, choice_type, choice_index):
        self.log("Performing %s:%s" % (choice_type, choice_index), logging.INFO)

        if choice_type == ChoiceType.MOVE:
            await self.choose_move(choice_index)
        elif choice_type == ChoiceType.SWITCH:
            await self.choose_switch(choice_index)
        else: pass  # Left in for future cases

        return await self.get_turn_actions(timeout=120)

    async def get_turn_actions(self, timeout=60, treat_error_as_loss=False):
        actions = []
        last_action = None
        wait_for_messages = True

        while wait_for_messages:
            msg = await self.get_next_message(timeout=timeout)

            if msg is None:
                break

            for line in msg.splitlines():
                if self.battle_id is None:
                    if ">battle-gen7" in line:
                        self.battle_id = line[1:]
                        continue

                action = Action.createAction(line)
                if action is None:
                    continue
                
                last_action = action

                if action.action_type == ActionType.REQUEST:
                    if action.params[1] != '':
                        self.last_request_json = json.loads(action.params[1])
                        self.rqid = self.last_request_json['rqid']

                        if 'forceSwitch' in self.last_request_json and self.last_request_json['forceSwitch'][0]:
                            self.log("Being forced switch", logging.INFO)
                            timeout=1.0
                    continue

                
                if action.is_terminating():
                    print("Terminating on ", last_action.action_type)
                    print(action.params)
                    wait_for_messages = False
                    break
                elif not action.is_logic_action():
                    actions.append(action)
                    action.encode()
        
        self.action_sequence = self.action_sequence + actions

        if last_action is None:
            return False
        elif last_action.action_type == ActionType.WIN:
            self.current_battle_state = BattleState.WIN
            return True
        elif last_action.action_type == ActionType.LOSS:
            self.current_battle_state = BattleState.LOSS
            return True
        elif last_action.action_type == ActionType.ERROR:
            if treat_error_as_loss:
                self.current_battle_state = BattleState.LOSS
                return True
            else:
                print("Found an error")
                print(last_action.params)
                return False
        elif 'forceSwitch' in self.last_request_json and self.last_request_json['forceSwitch'][0]:
            self.log("Need a switch!", logging.INFO)
            self.current_battle_state = BattleState.NEED_SWITCH
            return True
        else:
            self.current_battle_state = BattleState.ANY_ACTION
            return True


    async def choose_move(self, move_index):
        msg = "/choose move %d|%d" % (move_index, self.rqid)
        await self.ps_ws_client.send_message(self.battle_id, [msg])
    
    async def choose_switch(self, switch_index):
        msg = "/choose switch %d|%d" % (switch_index, self.rqid)
        await self.ps_ws_client.send_message(self.battle_id, [msg])
    
    async def perform_random_action(self):
        current_state = self.current_battle_state
        if self.current_battle_state == BattleState.ANY_ACTION:
            r = random.randint(1, 10)

            if r < 9:
                current_state = BattleState.NEED_MOVE
            else:
                current_state = BattleState.NEED_SWITCH


        if current_state == BattleState.NEED_SWITCH:
            switch_went_through = await self.choose_random_switch()
            if not switch_went_through:
                await self.choose_random_move()
        elif current_state == BattleState.NEED_MOVE:
            move_went_through = await self.choose_random_move()
            if not move_went_through:
                await self.choose_random_switch()
        
        # Otherwise the other bot hangs
        if self.current_battle_state == BattleState.NEED_SWITCH:
            await self.perform_random_action()
    
    async def choose_random_switch(self):
        options = [1, 2, 3, 4, 5, 6]
        random.shuffle(options)

        for option in options:
            went_through = await self.make_choice(ChoiceType.SWITCH, option)
            if went_through:
                return True
        return False

    async def choose_random_move(self):
        options = [1, 2, 3, 4]
        random.shuffle(options)

        for option in options:
            went_through = await self.make_choice(ChoiceType.MOVE, option)
            if went_through:
                return True
        return False


        