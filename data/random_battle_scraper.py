import requests
import os
from bs4 import BeautifulSoup
from git import Git

def random_battle_scraper(debug=False):
    # Specify which game mode is desired
    RANDOM_BATTLE_MODE = 'gen7randombattle'
    
    # Gets a list of user URLs to fetch games from
    user_urls = get_top_users(RANDOM_BATTLE_MODE, debug)
    
    # Init empty list for game tags
    game_tags = []
    
    # Iterate over each user and extend the list with their games
    for user in user_urls:
        game_tags.extend(get_game_tags(user, RANDOM_BATTLE_MODE, debug))

    # Cast as set to remove duplicates
    # Occurs when we have data from two players who have played eachother
    game_tags = set(game_tags)

    # Creates a directory for game data if it doesn't exist
    if not os.path.exists("games_data/"):
        os.makedirs("games_data/")

    print("---------------")
    # Sets repo for base game
    gitRepo = Git('./Pokemon-Showdown')
    # Iterate over each game and write its data to a file
    for game_tag in game_tags:
        write_to_file(gitRepo, game_tag)


def get_top_users(mode, debug=False):
    # Static URL for where top users are located
    LADDER_URL = 'https://pokemonshowdown.com/ladder/'

    # Perform and soup the request
    ladder_request = requests.get(LADDER_URL + mode) 
    soup = BeautifulSoup(ladder_request.text, 'html.parser')

    # Users are stored in a table
    user_rows = soup.find('table').find_all('tr')
    # First table row is trash
    user_rows.pop(0)

    # Init empty list of urls
    user_urls = []
    # Init i to keep track of users 
    i = 0

    # TODO: Replace with enumerate(?)
    for row in user_rows:
        # Obtain username
        username = row.find('a')['href'].replace('/users/', '')
        user_urls.append(username)

        if debug:
            print("User Found: {}".format(username))
            i = i + 1

            if i == 1:
                break

    return user_urls


def get_game_tags(user, mode, debug=False):
    # Static link for url to search players with
    SEARCH_URL = 'https://replay.pokemonshowdown.com/search/'
    
    # Init empty list of list items
    li_items = []

    if debug:
        print('Searching for {} played by {}'.format(mode, user))

    # Only two pages are available for any user, iterate with 1 and 2
    for i in range(1,3):
        # Create payload and send it off
        request_payload = {'user': user, 'page': i}
        user_request = requests.post(SEARCH_URL, request_payload)
        
        # Parse result and extend list with all list items
        soup = BeautifulSoup(user_request.text, 'html.parser')
        li_items.extend(soup.find_all('li'))

    if debug:
        print('Found {} list items'.format(len(li_items)))
    
    # Init game_tags list
    games_tags = []

    # Iterate over each list item and look for a hyper link
    for li in li_items:
        hrefURL = li.find('a')
        if hrefURL is None:
            continue
        hrefURL = hrefURL['href']
        # If hyper link, this is our user and we save the url in our list
        if mode in hrefURL:
            hrefURL = hrefURL.replace('/', '')
            games_tags.append(hrefURL)
            if debug:
                pass
    
    if debug:
        print('Filtered list down to {}'.format(len(games_tags)))

    return games_tags


def write_to_file(gitRepo, game_tag):
    # Get log from game
    logRequest = requests.get("https://replay.pokemonshowdown.com/" + game_tag + ".log")

    # Init seed as None for now
    seed = None
    
    # Iterate over log to look for seed
    for line in logRequest.iter_lines():
        # If seed is found, we set it as a string for now
        if "|seed|" in line:
            seed = line.replace("|seed|", "").replace(",", " ")
            seed = '"' + seed + '"'
        # If forfeited is found, we don't save anything
        elif "forfeited" in line:
            return
    
    # TODO: Allow any length
    if seed is None or len(seed.split(' ')) != 4:
        return

    # Request main page for replay and soup it
    mainRequest = requests.get("https://replay.pokemonshowdown.com/" + game_tag)
    mainSoup = BeautifulSoup(mainRequest.text, "html.parser")

    # Target the uploaddate to find when this match occurred
    date = mainSoup.find(class_="uploaddate").text
    date = date.replace("Uploaded: ", "").split(" | ")[0].lower()
    
    # Parses this info into something Git understands
    numericDate = getNumericDate(date)

    # Gets commit hash closest and before the date
    print("Writing")
    commitHash = gitRepo.rev_list('-n', '1', '--before="' + numericDate + '"', 'master')
    print(commitHash)

    # Checks out the main game to that date
    os.chdir("./Pokemon-Showdown/")
    gitRepo.checkout(commitHash)
    os.chdir("..")

    # Writes game to log
    f = open('games_data/' + game_tag, 'w+')
    f.write(logRequest.text.encode('utf-8'))
    f.close()

    print(seed)

    # Tells JS to provide more context to our logs
    os.system('node get_battle_context.js "' + 'games_data/' + game_tag + '" ' + seed)

def getNumericDate(dateStr):
    # Get rid of all commas
    dateStr = dateStr.replace(",", "")
    # Split upon the spaces
    month, day, year = dateStr.split(" ")

    # Get numeric value of date
    month = {
        'jan': '01',
        'feb': '02',
        'mar': '03',
        'apr': '04',
        'may': '05',
        'jun': '06',
        'jul': '07',
        'aug': '08',
        'sep': '09',
        'oct': '10',
        'nov': '11',
        'dec': '12',
    }.get(month)

    # Add a 0 to the date if its a single digit
    if len(day) == 1:
        day = '0' + day
    
    # Finishes off style of date string
    return year + '-' + month + '-' + day + ' 00:00'


def store_to_db(data):
    pass
