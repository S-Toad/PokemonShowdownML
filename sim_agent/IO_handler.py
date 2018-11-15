from subprocess import Popen, PIPE
import time
import os

class IOHandler():
    def __init__(self):
        self.path = os.path.realpath(__file__)
        self.path = os.path.join(self.path, "..", "..", "..")
        self.path = os.path.join(self.path, "Pokemon-Showdown", "pokemon-showdown")
        self.path = os.path.abspath(self.path)

        self.battleProccess = Popen(
            ["sh", self.path, "simulate-battle"], 
            stdin=PIPE, stdout=PIPE, bufsize=0
        )

        self.battleProccess.stdin.write(bytes('>start {"formatid": "gen7randombattle"}\n'.encode()))
        time.sleep(1)
        self.battleProccess.stdin.write(bytes('>player p1 {"name": "p1"}\n'.encode()))
        self.battleProccess.stdin.write(bytes('>player p2 {"name": "p2"}\n'.encode()))

        while True:
            x = self.battleProccess.stdout.readline()
            if x == bytes('\n'.encode()):
                break
            else:
                print(x)
        print("AAA")

        self.battleProccess.terminate()
    
    
IOHandler()