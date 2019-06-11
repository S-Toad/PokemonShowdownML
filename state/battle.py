import asyncio
import json
import random

from asyncio import TimeoutError
from enum import Enum
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
    SENT_CHOICE = 8

class ChoiceType(Enum):
    MOVE = 0
    SWITCH = 1


class BattleClient:
    current_battle_state = None
    action_sequence = None
    
    listen = False
    listen_thread = None
    
    websocket = None
    rqid = None
    battle_id = None

    username = None
    enemy = None

    team = None

    @property
    def url(self):
        return "https://play.pokemonshowdown.com/%s" % self.battle_id

    def __init__(self, websocket):
        self.websocket = websocket
        self.action_sequence = []
        self.current_battle_state = BattleState.STARTING_GAME
    
    def __eq__(self, obj):
        if isinstance(obj, BattleClient):
            return obj.current_battle_state == self.current_battle_state
        else:
            return obj == self.current_battle_state
    
    def __ne__(self, obj):
        return not self.__eq__(obj)
    
    
    async def make_choice(self, choice_type, choice_val):
        print("Choosing %s:%s" % (choice_type, choice_val))

        if choice_type == ChoiceType.MOVE:
            msg = "%s|/choose move %d|%d" % (self.battle_id, choice_val, self.rqid)
        elif choice_type == ChoiceType.SWITCH:
            msg = "%s|/choose switch %d|%d" % (self.battle_id, choice_val, self.rqid)
        else: pass  # Left in for future cases
        
        await self.websocket.send(msg)
        print("Set to waiting")
        self.current_battle_state = BattleState.SENT_CHOICE
    
    async def perform_random_action(self):
        r = random.randint(1, 10)
        switch_threshold = 9

        if r < switch_threshold:
            await self.perform_random_move()
        else:
            await self.perform_random_switch()
        
        print("Now waiting for updates")
        await self.wait_for_updates()

    
    async def wait_for_updates(self):
        await self.start_listen_for_actions()
        while self != BattleState.ANY_ACTION \
                and self != BattleState.NEED_MOVE \
                and self != BattleState.NEED_SWITCH \
                and self != BattleState.WAITING \
                and (self == BattleState.STARTING_GAME \
                    or self == BattleState.SENT_CHOICE):
            await asyncio.sleep(0)
        print("Broke because state is now: ", self.current_battle_state)
        await self.stop_listen_for_actions()

    async def perform_random_move(self):
        decision = ChoiceType.MOVE
        options = [1, 2, 3, 4]
        random.shuffle(options)

        for option_val in options:
            if self.can_make_move(option_val):
                await self.make_choice(decision, option_val)
                break


    async def perform_random_switch(self):
        decision = ChoiceType.SWITCH
        options = [1, 2, 3, 4, 5, 6]
        random.shuffle(options)

        for option_val in options:
            if self.can_make_switch(option_val):
                await self.make_choice(decision, option_val)
                break


    def can_make_move(self, move_index):
        return not self.team.is_move_disabled(move_index)
    
    def can_make_switch(self, choice_index):
        return self.team.is_switch_allowed(choice_index)

    async def start_listen_for_actions(self):
        self.listen = True
        self.listen_task = asyncio.create_task(self.listen_for_actions())
    
    async def stop_listen_for_actions(self):
        self.listen = False
        await self.listen_task

    async def listen_for_actions(self):
        while self.listen:
            msg = await self.receive_msg(timeout=0.01)

            if msg:
                for line in msg.splitlines():
                    if self.battle_id is None and ">battle-gen7" in line:
                        self.battle_id = line[1:]
                    else:
                        self.handle_action_msg(line)
    
    def handle_action_msg(self, line):
        action = Action.createAction(line)

        if action is None: return
        
        if action == ActionType.REQUEST:
            self.handle_request_action(action)
        elif action == ActionType.NEW_TURN:
            self.current_battle_state = BattleState.ANY_ACTION
        elif action == ActionType.WIN:
            self.current_battle_state = BattleState.WIN
        elif action == ActionType.LOSS:
            self.current_battle_state = BattleState.LOSS
        elif action ==  ActionType.ERROR:
            self.handle_error_action(action)
        elif action == ActionType.FAINT:
            self.current_battle_state = BattleState.NEED_SWITCH
        else:
            self.action_sequence.append(action)
    
    def handle_request_action(self, request_action):
        json_str = request_action.params[1]
        if json_str != '':

            request_dict = json.loads(json_str)
            self.rqid = request_dict['rqid']

            if 'forceSwitch' in request_dict and request_dict['forceSwitch'][0]:
                print("Setting state to needing a switch")
                self.current_battle_state = BattleState.NEED_SWITCH
            elif 'wait' in request_dict and request_dict['wait']:
                print('Setting state to waiting...')
                self.current_battle_state = BattleState.WAITING
            
            if self.team is None:
                print("Creating team")
                self.team = PokemonTeam(request_dict)
                print("Done creating team")
            else:
                print("Updating team...")
                self.team.update_from_dict(request_dict)
            
            print(request_dict)
    
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