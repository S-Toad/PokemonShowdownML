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
        player1.start_new_battle(battle_log='p1'), 
        player2.start_new_battle(battle_log='p2'))

    p1_battle = player1.current_battle
    p2_battle = player2.current_battle

    while p1_battle != BattleState.NEW_TURN \
            and p2_battle != BattleState.NEW_TURN:
        await asyncio.gather(
            p1_battle.flush_listen(),
            p2_battle.flush_listen())
    
    p1_side_encoding = p1_battle.get_side_encoding()
    p2_side_encoding = p2_battle.get_side_encoding()

    print("--------------------------------------------------------------------------")
    print("Battle started at: %s" % player1.current_battle.url)
    print("--------------------------------------------------------------------------")

    time.sleep(1)

    i = 1
    start = time.time()
    while not p1_battle.is_game_terminating() \
            or not p2_battle.is_game_terminating():
        print("\n\nStarting turn %d" % i)
        turn_start = time.time()

        player1.current_battle.encode()
        player2.current_battle.encode()
        

        p1_battle.set_available_actions()
        #p1_battle.start_listen_for_actions()

        p2_battle.set_available_actions()
        #p2_battle.start_listen_for_actions()
        while not p1_battle.is_turn_terminating() \
                or not p2_battle.is_turn_terminating():

            if p1_battle.can_take_action():
                await p1_battle.perform_random_action()
            if p2_battle.can_take_action():
                await p2_battle.perform_random_action()
            

            await asyncio.gather(
                p1_battle.flush_listen(),
                p2_battle.flush_listen())


        print("Finished turn %d" % i)

        turn_time = time.time() - turn_start
        print("Turn took %0.3f seconds" % turn_time)

        i+=1
    turn_time = time.time() - start

    winner = player1 if p1_battle == BattleState.WIN else player2
    print("%s won!" % winner.username)
    print("Battle took %0.3f seconds" % turn_time)


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
