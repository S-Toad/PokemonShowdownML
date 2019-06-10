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


async def challenge_me(username):
    bot = await ShowdownClient.createInstance()
    await bot.login()
    await bot.challenge_user(name=username)

    await bot.prepare_new_battle()

    i = 1
    while True:
        print("Starting turn %d" % i)
        i+=1
        await bot.perform_random_action()


async def main():

    #await challenge_me("sdsadsdas"); return


    player1, player2 = await asyncio.gather(
        ShowdownClient.createInstance(),
        ShowdownClient.createInstance())
    
    await asyncio.gather(
        player1.login(),
        player2.login())

    await player1.challenge_user(client=player2)
    await player2.accept_challenge()

    player1_actions, player2_actions = await asyncio.gather(
        player1.prepare_new_battle(),
        player2.prepare_new_battle())

    print("--------------------------------------------------------------------------")
    print("Battle started: https://play.pokemonshowdown.com/%s" % player1.battle_id)
    print("--------------------------------------------------------------------------")

    time.sleep(5)

    i = 1
    while True:
        print("Starting turn %d" % i)
        i+=1

        player1_actions, player1_actions = await asyncio.gather(
            player1.perform_random_action(),
            player2.perform_random_action())
        
        if player1.is_battle_over():
            break


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
