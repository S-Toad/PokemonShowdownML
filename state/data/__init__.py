import os 
import pickle


def load_pickle_and_numerate(file_name):
    base_path = os.path.dirname(os.path.realpath(__file__))
    file_path = os.path.join(base_path, file_name)
    
    print(file_path)

    data_dict = None
    with open(file_path, 'rb') as pkl_file:
        data_dict = pickle.load(pkl_file)
    
    i = 0
    for key in data_dict:
        i += 1
        data_dict[key]['index'] = i
    
    data_dict['COUNT'] = i
    
    return data_dict

def numerate_and_map_list(data_list):
    data_dict = {}
    i = 0
    for key in data_list:
        i += 1
        data_dict[key] = {'index' : i}
    
    data_dict['COUNT'] = i
    
    return data_dict


ability_dict = load_pickle_and_numerate('abilities.pkl')
pokedex_dict = load_pickle_and_numerate('pokedex.pkl')
move_dict = load_pickle_and_numerate('moves.pkl')
item_dict = load_pickle_and_numerate('items.pkl')

stat_list = ['atk', 'def', 'spa', 'spd', 'spe', 'accuracy', 'evasion']
stat_dict = numerate_and_map_list(stat_list)

status_list = ['psn', 'tox', 'brn', 'par', 'frz', 'slp']
status_dict = numerate_and_map_list(status_list)

weather_list = ['sunnyday', 'raindance', 'hail', 'primordialsea', 'sandstorm', 'deltastream']
weather_dict = numerate_and_map_list(weather_list)

side_list = ['auroraveil', 'firepledge', 'grasspledge', 'lightscreen', 'luckychant',
    'mist', 'reflect', 'safeguard', 'spikes', 'stealthrock', 'stickyweb', 'tailwind',
    'toxicspikes', 'waterpledge']
side_dict = numerate_and_map_list(side_list)

start_list = ['aquaring', 'attract', 'autotomize', 'bide', 'typechange', 'curse',
    'disable', 'doomdesire', 'embargo', 'focusenergy', 'foresight', 'typeadd',
    'futuresight', 'healblock', 'imprison', 'ingrain', 'laserfocus', 'leechseed',
    'magnetrise', 'mimic', 'miracleeye', 'nightmare', 'perish3', 'perish2', 'perish1',
    'perish0', 'powertrick', 'smackdown', 'stockpile', 'substitute', 'taunt', 'telekinesis',
    'throatchop', 'torment', 'uproar', 'yawn', 'confusion']
start_dict = numerate_and_map_list(start_list)

activate_list = ['aromaveil', 'battlebond', 'disguise', 'emergencyexit', 'flowerveil', 'forewarn',
    'healer', 'hydration', 'immunity', 'insomnia', 'lightningrod', 'limber', 'magmaarmor', 'mummy',
    'oblivious', 'owntempo', 'powerconstruct', 'shedskin', 'stickyhold', 'stormdrain', 'suctioncups',
    'sweetveil', 'symbiosis', 'synchronize', 'telepathy', 'vitalspirit', 'waterbubble', 'waterveil',
    'wimpout']
activate_dict = numerate_and_map_list(activate_list)
