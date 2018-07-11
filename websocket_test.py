
import asyncio
import time
from ShowdownWS import ShowdownWS

name = input("Please input a name: ")

ws = ShowdownWS(
    name,
    "http://localhost-8080.psim.us/",
    10
)

ws.beginConsole()