
import asyncio
import time
from ShowdownWS import ShowdownWS

name = input("Please input a name: ")

ws = ShowdownWS(
    name,
    "https://play.pokemonshowdown.com/",
    3
)

ws.beginConsole()