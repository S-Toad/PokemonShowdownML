import asyncio
import logging
import random
import re
import string
import time

from action import Action, ActionType
from queue import SimpleQueue
from showdown.websocket_communication import PSWebsocketClient

WEBSOCKET = "sim.smogon.com:8000"
RANDOM_BATTLE = "gen7randombattle"

class ShowdownClient:

    username = None
    ps_ws_client = None
    msg_queue = None

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
            mode=RANDOM_BATTLE, team='', register=False):
        
        if register:
            self.register_queue()
        
        if (client is not None and name is not None) \
                or (client is None and name is None):
            raise Exception("Client object xor name must be given.")
        
        if client is not None:
            name = client.username

        self.log("Attempting to challenge '%s'" % name)
        await self.ps_ws_client.challenge_user(name, mode, team)
    

    async def accept_challenge(self, mode=RANDOM_BATTLE, team='', register=False):
        if register:
            self.register_queue()

        self.log("Attempting to accept challenge")
        await self.ps_ws_client.accept_challenge(mode, team)
    

    def register_queue(self):
        if self.message_queue is None:
            self.ps_ws_client.message_queue = SimpleQueue()
    

    def deregister_queue(self):
        message_queue = self.ps_ws_client.message_queue
        self.ps_ws_client.message_queue = None

        return message_queue


    def log(self, msg, level=logging.INFO):
        msg = "%s : %s" % (self.username, msg)
        logging.log(level, msg)


    def gen_username(self, length=16):
        # Generates a string of some length using letters and digits
        characters = string.ascii_uppercase + string.digits
        self.username = ''.join(random.choices(characters, k=length))
    
    
    def get_battle_id_from_queue(self, deregister=True):
        battle_id = None
        rqid = None

        while not self.message_queue.empty() \
                and (battle_id is None):
            msg = self.message_queue.get()
            for line in msg.splitlines():
                if rqid is None:
                    match = re.match(r'\"rqid\":[0-9]', line)
                    
                    if match is not None:
                        print(match.group())
                    

                if battle_id is None and ">battle-gen7" in line:
                    battle_id = line[1:]
        
        if deregister:
            self.deregister_queue()
        
        self.battle_id = battle_id.strip()
        
        return battle_id
    

    async def get_next_message(self, timeout=0.1):
        try:
            msg = await asyncio.wait_for(
                self.ps_ws_client.receive_message(), timeout=timeout)
            return msg
        except asyncio.TimeoutError:
            return None
    

    async def get_turn_actions_from_queue(self, deregister=True):
        actions = await self.get_turn_actions(queue=self.msg_queue)

        if deregister:
            self.deregister_queue()
        
        return actions


    async def get_turn_actions(self, queue=None, register=False):
        actions = []
        new_turn = False

        if register:
            self.register_queue()

        while True:
            if queue:
                msg = None if queue.empty() else queue.get()
            else:
                msg = await self.get_next_message(timeout=10)
            
            if msg is None:
                break

            for line in msg.splitlines():
                action = Action.createAction(line)
                if action is not None:
                    action.encode()
                    actions.append(action)

                    # TODO: I believe we can just break here
                    if action.action_type == ActionType.NEW_TURN:
                        return actions

    async def choose_move(self, move_index):
        msg = "/choose move %d" % move_index

        await self.ps_ws_client.send_message(self.battle_id, [msg])
        