
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
import asyncio

class ShowdownWS:
    def __init__(self, username, URL, implicitWait):
        print("Initializing an instance using username: " + username)

        print("Loading driver")
        self.ws = webdriver.Firefox()
        self.ws.get(URL)
        self.ws.implicitly_wait(implicitWait)

        print("Attempting login")
        targetEl = self.ws.find_element_by_name("login")
        targetEl.click()

        print("Filling name")
        targetEl = self.ws.find_element_by_name("username") 
        targetEl.send_keys(username)

        print("Submitting")
        targetEl = self.ws.find_element_by_css_selector("button[type='submit']")
        targetEl.click()

        self.disconnect()
    
    def disconnect(self):
        return
        #self.url = self.ws.command_executor._url
        #self.session_id = self.ws.session_id

    def reconnect(self):
        return
        #self.ws = webdriver.Remote(command_executor=self.url)
        #self.ws.session_id = self.session_id

    # TODO: make async
    def asyncFindMatch(self):
        targetEl = self.ws.find_element_by_name("search")
        targetEl.click()

    def challenge(self, username):
        self.ws.find_element_by_name("finduser").click()
        targetEl = self.ws.find_element_by_name("data")

        targetEl.send_keys(username)
        targetEl.send_keys(webdriver.common.keys.Keys.RETURN)

        self.ws.find_element_by_name("challenge").click()
        self.ws.find_element_by_name("makeChallenge").click()

    def acceptChallenge(self):
        self.ws.find_element_by_name("acceptChallenge").click()
    
    def beginConsole(self):
        while True:
            result = input("What would you like to do?")
            result = result.split(" ")
            choice = result[0]

            self.reconnect()

            if choice == "a":
                self.asyncFindMatch()
            elif choice == "b":
                self.challenge(result[1])
            elif choice == "c":
                self.acceptChallenge()
            
            self.disconnect()
            