
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import StaleElementReferenceException, NoSuchElementException
from selenium.webdriver.common.action_chains import ActionChains

from Pokemon import Pokemon

from data.parseJSData import getPickle, DATA_TYPE

from enum import Enum
exit()
import time


DEFAULT_TIME_OUT = 20


class State(Enum):
    MAIN_MENU = 1
    QUEUED = 2
    WAITING_FOR_ACTION = 3
    WAITING_FOR_SWITCH = 4
    FINISHED = 5

class ShowdownWS:
    def __init__(self, username, URL, implicitWait):
        print("Initializing an instance using username: " + username)

        print("Loading Dicts")
        self.nameDict = getPickle(DATA_TYPE.POKE_DICT)
        self.abilDict = getPickle(DATA_TYPE.ABIL_DICT)
        self.moveDict = getPickle(DATA_TYPE.MOVE_DICT)
        self.itemDict = getPickle(DATA_TYPE.ITEM_DICT)

        print("Loading driver")
        self.ws = webdriver.Firefox()
        self.ws.implicitly_wait(implicitWait)
        self.ws.set_page_load_timeout(implicitWait)
        self.ws.get(URL)

        print("Attempting login")
        self.handle_click_by_name("login")

        print("Filling name")
        targetEl = self.ws.find_element_by_name("username") 
        targetEl.send_keys(username)

        print("Submitting")
        targetEl = self.ws.find_element_by_css_selector("button[type='submit']")
        targetEl.click()

    def check_pipe(self, time_out=DEFAULT_TIME_OUT):
        try:
            self.ws.find_element_by_class_name("logo")
            return True
        except (ConnectionAbortedError, BrokenPipeError):
            time_out = time_out - 1 
            if time_out == 0:
                return False
            else:
                return self.check_pipe(time_out)
    
    def handle_click_by_name(self, name, time_out=DEFAULT_TIME_OUT):
        try:
            targetEl = self.ws.find_element_by_name(name)
            try:
                targetEl.click()
                return True
            except StaleElementReferenceException:
                time_out = time_out - 1
        except NoSuchElementException:
            time_out = time_out - 1
        if time_out == 0:
            return False
        else:
            return self.handle_click_by_name(name, time_out)


    def findMatch(self, time_out=DEFAULT_TIME_OUT):
        self.check_pipe(time_out)
        self.handle_click_by_name("search")

    def challenge(self, username, time_out=DEFAULT_TIME_OUT):
        self.check_pipe(time_out)

        self.handle_click_by_name("finduser")
        
        targetEl = self.ws.find_element_by_name("data")
        targetEl.send_keys(username)
        targetEl.send_keys(webdriver.common.keys.Keys.RETURN)

        self.handle_click_by_name("challenge")
        self.handle_click_by_name("makeChallenge")
        self.skip_ahead()

    def acceptChallenge(self, time_out=DEFAULT_TIME_OUT):
        self.check_pipe(time_out)
        self.handle_click_by_name("acceptChallenge")
        self.skip_ahead()
    
    def get_initial_state(self, time_out=DEFAULT_TIME_OUT):
        self.check_pipe(time_out)

        pokemon_elements = [self.ws.find_element_by_name("chooseDisabled")]
        pokemon_elements.extend(self.ws.find_elements_by_name("chooseSwitch"))

        pkmnList = []

        pkmn = Pokemon(self.nameDict, self.itemDict, self.abilDict, self.moveDict)
        for poke_element in pokemon_elements:
            # Hovers over the element to reveal a tooltip
            ActionChains(self.ws).move_to_element(poke_element).perform()
            tooltip = self.ws.find_element_by_class_name("tooltip")

            # H2 tag contains name and level
            h2 = tooltip.find_element_by_tag_name("h2").text.split(" ")

            # If the length is 3, the pokemon has a special name
            # Form of [name, specialName, level] or [name, level]
            if len(h2) == 3:
                if "(" in h2[1]:
                    pkmn.setName(h2[1][1:-1])
                else:
                    pkmn.setName(h2[0] + h2[1])
                pkmn.setLevel(h2[2])
                #pokemonName = h2[1][1:-1]
                #pokemonLevel = h2[2].replace("L", "")
            else:
                pkmn.setName(h2[0])
                pkmn.setLevel(h2[1])
                #pokemonName = h2[0]
                #pokemonLevel = h2[1].replace("L", "")

            pokemonInfo = tooltip.find_elements_by_tag_name("p")

            # Health is in the form of: (a/b) where b is the max health
            healthString = pokemonInfo[0].text.split("/")[1].replace(")", "")
            pkmn.setMaxHP(healthString)

            # Next line is in the form of: "Ability: x / Item: y"
            # If no item is present, then itll be: "Ability: x"
            if "/" in pokemonInfo[1].text:
                pokemonAbility, pokemonItem = pokemonInfo[1].text.split(" / ")
                pkmn.setAbil(pokemonAbility.split(": ")[1])
                pkmn.setItem(pokemonItem.split(": ")[1])
            else:
                pkmn.setAbil(pokemonInfo[1].text.split(": ")[1])

            moveParagraph = pokemonInfo[3].text.replace("• ", "")
            moveLines = moveParagraph.split("\n")

            for move in moveLines:
                if ")" in move:
                    move = move[:move.rfind(" ")]
                pkmn.setMove(move)
            
            pkmnList.append(pkmn)
            pkmn = Pokemon(self.nameDict, self.itemDict, self.abilDict, self.moveDict)
        
        for a in pkmnList:
            a.print()

        return pkmnList


    def select_move(self, moveIndex):
        self.check_pipe()
        button = self.ws.find_element_by_css_selector('button[name="chooseMove"][value="%d"]' % moveIndex)
        button.click()
        return self.skip_ahead()
    
    def switch(self, switchIndex):
        self.check_pipe()
        button = self.ws.find_element_by_css_selector('button[name="chooseSwitch"][value="%d"]' % switchIndex)
        button.click()
        return self.skip_ahead()
    
    def skip_ahead(self, time_out=360):
        while True:
            result = self.handle_click_by_name("goToEnd")
            if result:
                return True
            time_out = time_out - 1
            if time_out == 0:
                return False
            time.sleep(500)
    
    def getState(self):
        self.check_pipe()

        if self.ws.find_element_by_name("search").size() > 0:
            return State.MAIN_MENU
        elif self.ws.find_element_by_name("cancelSearch").size() > 0:
            return State.QUEUED

    def beginConsole(self):
        while True:
            result = input("What would you like to do: ")
            result = result.split(" ")
            choice = result[0]

            print(result)

            if choice == "":
                continue
            elif choice == "f":
                self.findMatch()
            elif choice == "c":
                self.challenge(result[1])
            elif choice == "a":
                self.acceptChallenge()
            elif choice == "s":
                self.get_initial_state()
            elif choice == "m":
                self.select_move(int(result[1]))
            elif choice == "sw":
                self.switch(int(result[1]))
            
