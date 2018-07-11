
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import StaleElementReferenceException, NoSuchElementException
from selenium.webdriver.common.action_chains import ActionChains
import time


DEFAULT_TIME_OUT = 20


class ShowdownWS:
    def __init__(self, username, URL, implicitWait):
        print("Initializing an instance using username: " + username)

        print("Loading driver")
        self.ws = webdriver.Firefox()
        self.ws.implicitly_wait(implicitWait)
        self.ws.set_page_load_timeout(implicitWait)
        self.ws.get(URL)

        print("Attempting login")
        self.wait_for_element_to_click(self.handle_find_element_by_name("login"))

        print("Filling name")
        targetEl = self.handle_find_element_by_name("username") 
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
    
    def handle_click_find_element_by_name(self, name, time_out=DEFAULT_TIME_OUT):
        try:
            targetEl = self.ws.find_element_by_name(name)
            print("Found element %s" % name)
            return 
        except NoSuchElementException:
            print("Couldnt find %s" % name)
            time_out = time_out - 1
            if time_out == 0:
                return None

    def wait_for_element_to_click(self, element, time_out=DEFAULT_TIME_OUT):
        try:
            print("Trying to click")
            print(element)
            element.click()
            return True
        except StaleElementReferenceException:
            time_out = time_out - 1
            if time_out == 0:
                print("Failed")
                return False
            else:
                time.sleep(20/1000)
                return self.wait_for_element_to_click(element, time_out)


    def findMatch(self, time_out=DEFAULT_TIME_OUT):
        self.check_pipe(time_out)
        self.wait_for_element_to_click(self.handle_find_element_by_name("search"))

    def challenge(self, username, time_out=DEFAULT_TIME_OUT):
        self.check_pipe(time_out)

        self.wait_for_element_to_click(self.handle_find_element_by_name("finduser"))
        
        targetEl = self.handle_find_element_by_name("data")
        targetEl.send_keys(username)
        targetEl.send_keys(webdriver.common.keys.Keys.RETURN)

        self.wait_for_element_to_click(self.handle_find_element_by_name("challenge"))
        self.wait_for_element_to_click(self.handle_find_element_by_name("makeChallenge"))

    def acceptChallenge(self, time_out=DEFAULT_TIME_OUT):
        self.check_pipe(time_out)
        self.wait_for_element_to_click(self.handle_find_element_by_name("acceptChallenge"))
    
    def get_initial_state(self, time_out=DEFAULT_TIME_OUT):
        self.check_pipe(time_out)

        pokemon_elements = [self.handle_find_element_by_name("chooseDisabled")]
        pokemon_elements.extend(self.handle_find_element_by_name("chooseSwitch"))

        print(len(pokemon_elements))

        for poke_element in pokemon_elements:
            pokemonName = None
            pokemonLevel = None
            pokemonHP = None
            pokemonAbility = None
            pokemonItem = None
            pokemonMoves = None

            ActionChains(self.ws).move_to_element(poke_element).perform()
            tooltip = self.ws.find_element_by_class_name("tooltip")

            h2 = tooltip.find_element_by_tag_name("h2").text.split(" ")
            if len(h2) == 3:
                pokemonName = h2[1][1:-1]
                pokemonLevel = h2[2].replace("L", "")
            else:
                pokemonName = h2[0]
                pokemonLevel = h2[1].replace("L", "")


            lines = tooltip.find_elements_by_tag_name("p")

            pokemonHP = lines[0].text.split("/")[1].replace(")", "")

            if "/" in lines[1].text:
                pokemonAbility, pokemonItem = lines[1].text.split(" / ")
                pokemonAbility = pokemonAbility.split(": ")[1]
                pokemonItem = pokemonItem.split(": ")[1]
            else:
                pokemonAbility = lines[1].text.split(": ")[1]
                pokemonItem = ""

            mm = lines[3].text.replace("• ", "")
            mm = mm.split("\n")
            pokemonMoves = []

            for move in mm:
                if ")" in move:
                    move = move[:move.rfind(" ")]
                pokemonMoves.append(move)

            print("Pokemon: %s" % pokemonName)
            print("Level: %s" % pokemonLevel)
            print("Max HP: %s" % pokemonHP)
            print("Ability: %s" % pokemonAbility)
            print("Item: %s" % pokemonItem)
            print("Move: %s" % pokemonMoves)

    def select_move(self, moveIndex):
        print("button[value=%d]" % moveIndex)
        button = self.ws.find_element_by_css_selector('button[value="%d"]' % moveIndex)
        self.wait_for_element_to_click(button)

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
            elif choice in "1234":
                self.select_move(int(choice))
            
