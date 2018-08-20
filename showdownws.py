from enum import Enum
from data.parseJSData import getPickle, DATA_TYPE

import time
import random
import copy

from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import StaleElementReferenceException, NoSuchElementException
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from data.logdata import ActionType, get_action_type, is_valid_log
from data.GameState.GameState import GameState

class State(Enum):
    MAIN_MENU = 1
    QUEUED = 2
    CHALLENGED = 3
    WAITING_FOR_ACTION = 4
    WAITING_FOR_SWITCH = 5
    WAITING_FOR_ATTACK = 6
    MATCH_FINISHED = 7
    CHALLENGING = 8
    WAITING_FOR_OPPONENT = 9
    SHOWING_RESULT = 10

class ShowdownWS:
    def __init__(self, URL, username):
        print("Initializing an instance using username: " + username)
        
        self.nameDict = getPickle(DATA_TYPE.POKE_DICT)
        self.abilDict = getPickle(DATA_TYPE.ABIL_DICT)
        self.moveDict = getPickle(DATA_TYPE.MOVE_DICT)
        self.itemDict = getPickle(DATA_TYPE.ITEM_DICT)

        desired = DesiredCapabilities.CHROME
        desired['loggingPrefs'] = {'browser': 'ALL'}

        self.username = username

        print("Loading driver")
        self.ws = webdriver.Chrome(desired_capabilities=desired)
        self.ws.set_page_load_timeout(30)
        self.ws.get(URL)

        self.login(username)


    def check_pipe(self, time_out=2):
        try:
            self.ws.find_element_by_class_name("logo")
            time.sleep(0.1)
            return True
        except (ConnectionAbortedError, BrokenPipeError):
            time_out = time_out - 1 
            if time_out == 0:
                return False
            else:
                time.sleep(0.25)
                return self.check_pipe(time_out)

    def login(self, username):
        try:
            WebDriverWait(self.ws, 10).until(EC.element_to_be_clickable((By.NAME, "login"))).click()
        except:
            self.ws.quit()

        targetEl = self.ws.find_element_by_name("username")
        targetEl.send_keys(username)
        targetEl.send_keys(Keys.RETURN)

    def get_state(self, i=0):
        self.check_pipe()

        try:
            self.ws.find_element_by_name("acceptChallenge")
            return State.CHALLENGED
        except NoSuchElementException: pass

        try:
            self.ws.find_element_by_name("cancelChallenge")
            return State.CHALLENGING
        except NoSuchElementException: pass

        try:
            self.ws.find_element_by_name("cancelSearch")
            return State.QUEUED
        except NoSuchElementException: pass
        
        try:
            self.ws.find_element_by_name("goToEnd")
            return State.SHOWING_RESULT
        except NoSuchElementException: pass
        
        try:
            self.ws.find_element_by_name("closeAndMainMenu")
            return State.MATCH_FINISHED
        except NoSuchElementException: pass

        canSwitch = False
        canAttack = False

        try:
            self.ws.find_element_by_name("chooseSwitch")
            canSwitch = True
        except NoSuchElementException: pass
        
        try:
            self.ws.find_element_by_name("chooseMove")
            canAttack = True
        except NoSuchElementException: pass

        if canSwitch and canAttack:
            return State.WAITING_FOR_ACTION
        elif canSwitch:
            return State.WAITING_FOR_SWITCH
        elif canAttack:
            return State.WAITING_FOR_ATTACK

        if "Waiting for opponent..." in self.ws.page_source:
            return State.WAITING_FOR_OPPONENT

        if i == 3:
            return State.MAIN_MENU
        else:
            time.sleep(0.1)
            return self.get_state(i=i+1)
    
    def challenge_user(self, user):
        try:
            WebDriverWait(self.ws, 10).until(EC.element_to_be_clickable((By.NAME, "finduser"))).click()
        except:
            self.ws.quit()
        
        targetEl = self.ws.find_element_by_name("data")
        targetEl.send_keys(user)
        targetEl.send_keys(Keys.RETURN)

        try:
            WebDriverWait(self.ws, 10).until(EC.element_to_be_clickable((By.NAME, "challenge"))).click()
            WebDriverWait(self.ws, 10).until(EC.element_to_be_clickable((By.NAME, "makeChallenge"))).click()
        except:
            self.ws.quit()

    
    def accept_challenge(self):
        try:
            WebDriverWait(self.ws, 10).until(EC.element_to_be_clickable((By.NAME, "acceptChallenge"))).click()
            time.sleep(1)
        except:
            self.ws.quit()
    
    def return_to_main_menu(self):
        try:
            self.ws.execute_script("window.history.go(-1)")
            WebDriverWait(self.ws, 2).until(EC.element_to_be_clickable((By.NAME, "closeRoom"))).click()
        except NoSuchElementException:
            print("Cant click")
            self.ws.quit()
    
    def skip_ahead(self):
        self.ws.find_element_by_name("goToEnd").click()
    
    def decide_action(self):
        if random.randint(1, 10) <= 9:
            #print("Choosing Move")
            self.choose_move()
        else:
            #print("Choosing Switch")
            self.choose_switch()

    def choose_move(self):
        try:
            WebDriverWait(self.ws, 10).until(EC.element_to_be_clickable((By.NAME, "chooseMove")))
        except:
            self.ws.quit()
        
        buttons = self.ws.find_elements_by_name("chooseMove")
        options = []
        for button in buttons:
            val = button.get_attribute("value")
            if val is not None:
                options.append(val)
        
        moveIndex = 0
        while True:
            moveIndex = random.randint(1, 4)
            if str(moveIndex) in options:
                break

        
        self.ws.find_element_by_css_selector('button[name="chooseMove"][value="%d"]' % moveIndex).click()

    def choose_switch(self):
        try:
            WebDriverWait(self.ws, 10).until(EC.element_to_be_clickable((By.NAME, "chooseSwitch")))
        except:
            self.ws.quit()

        buttons = self.ws.find_elements_by_name("chooseSwitch")
        options = []
        for button in buttons:
            val = button.get_attribute("value")
            if val is not None:
                options.append(val)
        
        switchIndex = 0
        while True:
            switchIndex = random.randint(1, 5)
            if str(switchIndex) in options:
                break
        
        self.ws.find_element_by_css_selector('button[name="chooseSwitch"][value="%d"]' % switchIndex).click()
    
    def process_turn(self, gs):
        log = self.ws.get_log('browser')

        validTurnData = []

        for logItem in log:

            message = logItem['message']

            teamJSON = ""
            if "|request|" in message and "{" in message:
                    teamJSON = message.split("|request|")[1]
                    teamJSON = teamJSON.replace("\\", "")
                    teamJSON = teamJSON[:-1]
                    teamJSON = teamJSON.replace("true", "True")
                    teamJSON = teamJSON.replace("false", "False")
                    teamJSON = teamJSON.replace("null", "None")

            if gs is None and teamJSON != "":
                print("New Match being made, generating new game state")
                gs = self.create_initial_game_state(teamJSON)
            elif gs is not None:
                gs.teamJSON = teamJSON

            if is_valid_log(message):
                validTurnData.append(message)
        
        gs = gs.parse_round(validTurnData)

        return gs


    def create_initial_game_state(self, requestString):
        gs = GameState(
            requestString,
            self.nameDict,
            self.itemDict,
            self.abilDict,
            self.moveDict
        )

        return gs

    def automate(self, timeStep, challengeUser="", wait=False):
        gs = None
        while True:            
            pokeState = self.get_state()

            if pokeState == State.MAIN_MENU:
                if challengeUser != "":
                    self.ws.get_log('browser')
                    self.challenge_user(challengeUser)
            elif pokeState == State.CHALLENGED:
                self.ws.get_log('browser')
                self.accept_challenge()
            elif pokeState == State.CHALLENGING: pass
            elif pokeState == State.MATCH_FINISHED:
                gs = self.process_turn(gs)
                if wait:
                    gs.print_info()
                    input("Press a button to continue...")
                time.sleep(10000)
                time.sleep(1)
                self.return_to_main_menu()
                time.sleep(1)
                gs = None
            elif pokeState == State.WAITING_FOR_ACTION:
                gs = self.process_turn(gs)
                if wait:
                    gs.print_info()
                    input("Press a button to continue...")
                self.decide_action()
            elif pokeState == State.WAITING_FOR_SWITCH:
                gs = self.process_turn(gs)
                if wait:
                    gs.print_info()
                    input("Press a button to continue...")
                self.choose_switch()
            elif pokeState == State.WAITING_FOR_ATTACK:
                gs = self.process_turn(gs)
                if wait:
                    gs.print_info()
                    input("Press a button to continue...")
                self.choose_move()
            elif pokeState == State.SHOWING_RESULT:
                self.skip_ahead()

            time.sleep(timeStep)



    def console(self):
        while True:
            result = input("What would you like to do: ")
            result = result.split(" ")
            choice = result[0]

            print(result)

            if choice == "":
                continue
            elif choice == "s":
                print(self.get_state())
            elif choice == "auto":
                if len(result) == 2:
                    self.automate(0.01, challengeUser=result[1])
                else:
                    self.automate(0.01)
            elif choice == "autowait":
                if len(result) == 2:
                    self.automate(0.01, challengeUser=result[1], wait=True)
                else:
                    self.automate(0.01)
