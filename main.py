import asyncio
import logging
import random
import string
import time

from concurrent.futures import ProcessPoolExecutor
from config import logger
from showdown.websocket_communication import PSWebsocketClient
from showdownclient import ShowdownClient
from state.battle import BattleState

WEBSOCKET = "sim.smogon.com:8000"
MODE = "gen7randombattle"


async def challenge_me(username):
    bot = await ShowdownClient.createInstance()
    await bot.login()
    await bot.challenge_user(name=username)
    await bot.prepare_new_battle()

    for i in range(200):
        print("Starting turn %d" % i)

        # current_battle <-> battle_state

async def test():
    for i in range(10):
        await asyncio.sleep(1)
        print(i)


async def main():
    player1, player2 = await asyncio.gather(
        ShowdownClient.createInstance(),
        ShowdownClient.createInstance())
    
    await asyncio.gather(
        player1.login(),
        player2.login())
    
    await player1.challenge_user(client=player2)
    time.sleep(0.5)
    await player2.accept_challenge()
    

    await asyncio.gather(
        player1.start_new_battle(), 
        player2.start_new_battle())

    await asyncio.gather(
        player1.current_battle.wait_for_updates(),
        player2.current_battle.wait_for_updates())

    print("--------------------------------------------------------------------------")
    print("Battle started: %s" % player1.current_battle.url)
    print("--------------------------------------------------------------------------")

    time.sleep(1)

    i = 1
    while True:
        print("\n\nStarting turn %d" % i)

        print("Starting the initial actions...")

        await asyncio.gather(
            player1.current_battle.perform_random_action(),
            player2.current_battle.perform_random_action())
        
        while player1.current_battle == BattleState.NEED_SWITCH \
                or player2.current_battle == BattleState.NEED_SWITCH:
            
            if player1.current_battle == BattleState.NEED_SWITCH:
                print("Player 1 needs to switch")
                await player1.current_battle.perform_random_switch()
            
            if player2.current_battle == BattleState.NEED_SWITCH:
                print("Player 2 needs to switch")
                await player2.current_battle.perform_random_switch()
            
            await asyncio.gather(
                player1.current_battle.wait_for_updates(),
                player2.current_battle.wait_for_updates())
        
        print("Done waiting for initial action")
        
        print("Finished turn %d" % i)

        i+=1
        time.sleep(5)


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
