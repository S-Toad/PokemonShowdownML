import requests
from bs4 import BeautifulSoup

def random_battle_scraper(debug=False):
    RANDOM_BATTLE_MODE = 'gen7randombattle'
    
    user_urls = get_top_users(RANDOM_BATTLE_MODE, debug)
    
    game_urls = []
    for user in user_urls:
        game_urls.extend(get_game_urls(user, RANDOM_BATTLE_MODE, debug))
        break
    


def get_top_users(mode, debug=False):
    LADDER_URL = 'https://pokemonshowdown.com/ladder/'

    ladder_request = requests.get(LADDER_URL + mode)  # Perform request
    soup = BeautifulSoup(ladder_request.text, 'html.parser')  # Soup the request

    user_rows = soup.find('table').find_all('tr')  # Users are stored in a table
    user_rows.pop(0)  # First table row is trash

    user_urls = []
    for row in user_rows:
        # Obtain username
        username = row.find('a')['href'].replace('/users/', '')
        user_urls.append(username)

        if debug:
            print("User Found: {}".format(username))
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
    
    game_tags = []
    for li in li_items:
        hrefURL = li.find('a')['href']
        if mode in hrefURL:
            hrefURL = hrefURL.replace('/', '')
            game_tags.append(hrefURL)
            if debug:
                print("Filtered {}".format(hrefURL))
    
    if debug:
        print("Filtered list down to {}".format(len(hrefURL)))

    return game_tags

def store_to_db(data):
    pass
