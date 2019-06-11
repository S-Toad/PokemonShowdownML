import asyncio
import json
import logging
import random
import re
import string
import time

from state.battle import BattleClient, BattleState, ChoiceType
from enum import Enum
from queue import SimpleQueue
from showdown.websocket_communication import PSWebsocketClient

WEBSOCKET = "sim.smogon.com:8000"
RANDOM_BATTLE = "gen7randombattle"

class ShowdownClient:

    username = None
    ps_ws_client = None
    action_sequence = None
    battle_id = None
    rqid = None
    last_request_json = None

    current_battle = None

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
    


    async def login(self):
        self.log("Logging in")
        await self.ps_ws_client.login()
        self.log("Done logging in")
    
    async def start_new_battle(self, battle_log=None):
        self.log("Starting a new battle")
        self.current_battle = BattleClient(self.ps_ws_client.websocket,
            battle_log=battle_log)
    

    async def challenge_user(self, client=None, name=None,
            mode=RANDOM_BATTLE, team=''):
        
        if (client is not None and name is not None) \
                or (client is None and name is None):
            raise Exception("Client object xor name must be given.")
        
        if client is not None:
            name = client.username

        self.log("Attempting to challenge '%s'" % name)
        await self.ps_ws_client.challenge_user(name, mode, team)
    
    # TODO: Should hang until challenge is accepted
    async def accept_challenge(self, mode=RANDOM_BATTLE, team=''):
        self.log("Attempting to accept challenge")
        await self.ps_ws_client.accept_challenge(mode, team)


    def log(self, msg, level=logging.INFO):
        msg = "%s : %s" % (self.username, msg)
        logging.log(level, msg)


    def gen_username(self, length=16):
        # Generates a string of some length using letters and digits
        characters = string.ascii_uppercase + string.digits
        self.username = ''.join(random.choices(characters, k=length))
