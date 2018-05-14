import requests
import os
from bs4 import BeautifulSoup
from git import Git

def random_battle_scraper(debug=False):
    RANDOM_BATTLE_MODE = 'gen7randombattle'
    
    user_urls = get_top_users(RANDOM_BATTLE_MODE, debug)
    
    game_urls = []
    for user in user_urls:
        game_urls.extend(get_game_urls(user, RANDOM_BATTLE_MODE, debug))

    game_urls = set(game_urls)  # Remove duplicates

    if not os.path.exists("games_data/"):
        os.makedirs("games_data/")

    print("---------------")
    gitRepo = Git('./Pokemon-Showdown')
    for game_url in game_urls:
        write_to_file(gitRepo, game_url)
    



def get_top_users(mode, debug=False):
    LADDER_URL = 'https://pokemonshowdown.com/ladder/'

    ladder_request = requests.get(LADDER_URL + mode)  # Perform request
    soup = BeautifulSoup(ladder_request.text, 'html.parser')  # Soup the request

    user_rows = soup.find('table').find_all('tr')  # Users are stored in a table
    user_rows.pop(0)  # First table row is trash

    user_urls = []
    i = 0
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


def get_game_urls(user, mode, debug=False):
    SEARCH_URL = 'https://replay.pokemonshowdown.com/search/'
    li_items = []

    if debug:
        print('Searching for {} played by {}'.format(mode, user))

    for i in range(1,3):
        request_payload = {'user': user, 'page': i}
        user_request = requests.post(SEARCH_URL, request_payload)
        
        soup = BeautifulSoup(user_request.text, 'html.parser')
        li_items.extend(soup.find_all('li'))

    if debug:
        print('Found {} list items'.format(len(li_items)))
    
    game_urls = []
    for li in li_items:
        hrefURL = li.find('a')
        if hrefURL is None:
            continue
        hrefURL = hrefURL['href']
        if mode in hrefURL:
            hrefURL = hrefURL.replace('/', '')
            game_urls.append(hrefURL)
            if debug:
                pass
    
    if debug:
        print('Filtered list down to {}'.format(len(game_urls)))

    return game_urls


def write_to_file(gitRepo, game_url):
    logRequest = requests.get("https://replay.pokemonshowdown.com/" + game_url + ".log")

    seed = None
    for line in logRequest.iter_lines():
        if "|seed|" in line:
            seed = line.replace("|seed|", "").replace(",", " ")
            seed = '"' + seed + '"'
        elif "forfeit" in line:
            return
    
    if seed is None or len(seed.split(' ')) != 4:
        return


    mainRequest = requests.get("https://replay.pokemonshowdown.com/" + game_url)
    mainSoup = BeautifulSoup(mainRequest.text, "html.parser")
    date = mainSoup.find(class_="uploaddate").text
    date = date.replace("Uploaded: ", "").split(" | ")[0].lower()
    
    numericDate = getNumericDate(date)

    print("Writing")
    commitHash = gitRepo.rev_list('-n', '1', '--before="' + numericDate + '"', 'master')
    print(commitHash)
    os.chdir("./Pokemon-Showdown/")
    gitRepo.checkout(commitHash)
    os.chdir("..")

    f = open('games_data/' + game_url, 'w+')
    f.write(logRequest.text.encode('utf-8'))
    f.close()
    os.system('node get_battle_context_new.js "' + 'games_data/' + game_url + '" ' + seed)

def getNumericDate(dateStr):
    dateStr = dateStr.replace(",", "")
    month, day, year = dateStr.split(" ")

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

    if len(day) == 1:
        day = '0' + day
    
    return year + '-' + month + '-' + day + ' 00:00'


def store_to_db(data):
    pass
