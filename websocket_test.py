
import asyncio
import time
from showdownws import ShowdownWS

name = input("Please input a name: ")

ws = ShowdownWS(
    "http://localhost-8080.psim.us/",
    name
)

ws.console()
