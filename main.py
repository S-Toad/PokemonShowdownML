import asyncio
import logging
import random
import string
import time

from action import ActionType
from config import logger
from showdown.websocket_communication import PSWebsocketClient
from showdownclient import ShowdownClient

WEBSOCKET = "sim.smogon.com:8000"
MODE = "gen7randombattle"

async def main():

    #player1 = await ShowdownClient.createInstance()
    #player2 = await ShowdownClient.createInstance()


    player1, player2 = await asyncio.gather(
        ShowdownClient.createInstance(),
        ShowdownClient.createInstance())
    
    await asyncio.gather(
        player1.login(),
        player2.login())

    await player1.challenge_user(client=player2)
    await player2.accept_challenge()

    player1_actions, player2_actions = await asyncio.gather(
        player1.get_initial_actions(),
        player2.get_initial_actions())

    print("--------------------------------------------------")
    print("Battle started: https://play.pokemonshowdown.com/%s" % player1.battle_id)
    print("--------------------------------------------------")

    time.sleep(5)

    for i in range(3):
        
        print("Starting turn %d" % i)
        # TODO: These don't depend on eachother
        # We can run them both and wait for both to be done

        await player1.choose_move(1)
        await player2.choose_move(1)

        player1_actions, player2_actions = await asyncio.gather(
            player1.get_turn_actions(),
            player2.get_turn_actions())

    #print("--------------")
    #await player1.get_turn_actions()

if __name__ == "__main__":
    # Set lowest level
    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)

    formatter = logging.Formatter("%(name)s : %(levelname)s : %(message)s")

    # Print to console at level info
    consoleHandler = logging.StreamHandler()
    consoleHandler.setLevel(logging.INFO)
    consoleHandler.setFormatter(formatter)
    logger.addHandler(consoleHandler)

    # Write to file at level debug
    fileHandler = logging.FileHandler('showdown.log', mode='w')
    fileHandler.setLevel(logging.DEBUG)
    fileHandler.setFormatter(formatter)
    logger.addHandler(fileHandler)

    asyncio.get_event_loop().run_until_complete(main())
