
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
import asyncio

class ShowdownWS:
    def __init__(self, username, URL, implicitWait):
        print("Initializing an instance using username: " + username)

        print("Loading driver")
        self.ws = webdriver.Firefox()
        self.ws.implicitly_wait(implicitWait)
        self.ws.set_page_load_timeout(implicitWait)
        self.ws.get(URL)

        print("Attempting login")
        targetEl = self.ws.find_element_by_name("login")
        targetEl.click()

        print("Filling name")
        targetEl = self.ws.find_element_by_name("username") 
        targetEl.send_keys(username)

        print("Submitting")
        targetEl = self.ws.find_element_by_css_selector("button[type='submit']")
        targetEl.click()

    def findMatch(self):
        try:
            targetEl = self.ws.find_element_by_name("search")
            targetEl.click()
        except BrokenPipeError:
            self.findMatch()

    def challenge(self, username):
        try:
            self.ws.find_element_by_name("finduser").click()
            targetEl = self.ws.find_element_by_name("data")

            targetEl.send_keys(username)
            targetEl.send_keys(webdriver.common.keys.Keys.RETURN)

            self.ws.find_element_by_name("challenge").click()
            self.ws.find_element_by_name("makeChallenge").click()
        except BrokenPipeError:
            self.challenge(username)

    def acceptChallenge(self):
        try:
            self.ws.find_element_by_name("acceptChallenge").click()
        except BrokenPipeError:
            self.acceptChallenge()
    
    def get_status(self):
        pass
    
    def select_move(self, moveIndex):
        pass

    def beginConsole(self):
        while True:
            result = input("What would you like to do: ")
            result = result.split(" ")
            choice = result[0]

            if choice == "f":
                self.findMatch()
            elif choice == "c":
                self.challenge(result[1])
            elif choice == "a":
                self.acceptChallenge()
            elif choice == "s":
                self.get_status()
            elif choice in "1234":
                self.select_move(int(choice))
            
