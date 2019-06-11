



class PokemonTeam:
    pokemons = []
    pokemon_map = {}
    active_moves = {}

    def __init__(self, request_dict):
        self.pokemons = []
        self.pokemon_map = {}
        self.active_moves = {}

        for poke_dict in request_dict['side']['pokemon']:
            poke = Pokemon(poke_dict)
            self.pokemon_map[poke.name] = poke
            self.pokemons.append(poke)
        
        self.active_moves = request_dict['active'][0]['moves']
        
    def update_from_dict(self, request_dict):
        for poke_dict in request_dict['side']['pokemon']:
            poke_name = poke_dict['details'].split(', ')[0]
            self.pokemon_map[poke_name].update_from_dict(poke_dict)
        
        if 'active' in request_dict:
            self.active_moves = request_dict['active'][0]['moves']

    def is_move_disabled(self, index):
        return self.active_moves[index-1]['disabled']
    
    def is_switch_allowed(self, index):
        return not self.pokemons[index-1].is_active()

class Pokemon:    
    name = None
    level = None
    gender = None
    
    curr_health = None
    max_health = None
    condition = None
    
    attack = None
    defense = None
    special_attack = None
    special_defense = None
    speed = None

    ability = None
    item = None

    active = None
    moves = None
    

    def __init__(self, request_dict):
        details = request_dict['details'].split(', ')
        self.name = details[0]
        self.level = details[1]

        c_health, m_health = request_dict['condition'].split('/')
        self.curr_health = int(c_health)
        self.m_health = int(m_health)

        self.attack = request_dict['stats']['atk']
        self.defense = request_dict['stats']['def']
        self.special_attack = request_dict['stats']['spa']
        self.special_defense = request_dict['stats']['spd']
        self.speed = request_dict['stats']['spe']

        self.ability = request_dict['ability']
        self.item = request_dict['item']

        self.active = request_dict['active']
        
        self.moves = []
        for move_name in request_dict['moves']:
            self.moves.append(move_name)

        
    
    def update_from_dict(self, request_dict):
        condition_str = request_dict['condition']
        if ' ' in condition_str:
            print(condition_str)
        else:
            self.curr_health = int(condition_str.split('/')[0])

        self.ability = request_dict['ability']
        self.item = request_dict['item']
        self.active = request_dict['active']
    
    def is_fainted(self):
        return self.curr_health == 0
    
    def is_active(self):
        return self.active
