from subprocess import Popen, PIPE
from queue import Queue, Empty
from threading import Thread
from util import enqueue_output
import time
import os
import sys

#ON_POSIX = 'posix' in sys.builtin_module_names

class IOHandler():
    def __init__(self, delay=0.2):
        self.delay = delay
        self.path = os.path.abspath(os.path.join(
            os.path.realpath(__file__), 
            "..", "..", "..", 
            "Pokemon-Showdown", "pokemon-showdown"))

        self.process = Popen(
            ["sh", self.path, "simulate-battle"],
            stdin=PIPE, stdout=PIPE, bufsize=0)
        self.process.stdin.write(b'>start {"formatid": "gen7randombattle"}\n')
        self.process.stdin.write(b'>player p1 {"name": "p1"}\n')
        self.process.stdin.write(b'>player p2 {"name": "p2"}\n')

        self.outQueue = Queue()
        self.outThread = Thread(
            target=enqueue_output,
            args=(self.process.stdout, self.outQueue)
        )
        self.outThread.daemon = True
        self.outThread.start()

    def get_output(self):
        out = ""

        while True:
            if self.outQueue.empty():
                time.sleep(self.delay)
                if self.outQueue.empty():
                    return out
            out += self.outQueue.get_nowait().decode()
        
        return out
    
    def terminate(self):
        self.process.terminate()

    
ioHandler = IOHandler()

while True:
    a = ioHandler.get_output()
    if a == "":
        time.sleep(1)
    else:
        sys.stdout.write(a)
        sys.stdout.flush()
