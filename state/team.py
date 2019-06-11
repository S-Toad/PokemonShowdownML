



class PokemonTeam:
    pokemons = []
    pokemon_map = {}
    active_dict = {}

    def __init__(self, request_dict):
        self.pokemons = []
        self.pokemon_map = {}
        self.active_dict = {}

        index = 1
        for poke_dict in request_dict['side']['pokemon']:
            poke = Pokemon(poke_dict)
            poke.index = index
            poke.curr_index = index
            index += 1
            self.pokemon_map[poke.name] = poke
            self.pokemons.append(poke)
        
        #print("Mapped choice_index up to %d" % choice_index)
        
        self.active_dict = request_dict['active'][0]
        
    def update_from_dict(self, request_dict):
        curr_index = 1
        for poke_dict in request_dict['side']['pokemon']:
            poke_name = poke_dict['ident'].split(' ')[1]
            poke = self.pokemon_map[poke_name]
            poke.curr_index = curr_index
            curr_index += 1
            poke.update_from_dict(poke_dict)
        
        #print("Mapped choice_index up to %d" % choice_index)
        
        if 'active' in request_dict:
            self.active_dict = request_dict['active'][0]

    def is_move_allowed(self, choice_index):
        # If 4 moves aren't available for some reason
        # E.g, outrage
        if (choice_index-1) >= len(self.active_dict['moves']):
            print("Move is out of range")
            return False
        print("Trying move index of %d" % (choice_index-1))
        move_dict = self.active_dict['moves'][choice_index-1]
        return ('disabled' not in move_dict) or not move_dict['disabled']
    
    def switch_available(self):
        if 'trapped' in self.active_dict and self.active_dict['trapped']:
            return False

        for poke in self.pokemons:
            if poke.is_switch_allowed():
                return True
        return False
    
    def get_poke_choice_index_if_valid(self, index):
        poke = self.get_poke_from_index(index)
        if poke.is_switch_allowed():
            return poke.curr_index
        else:
            return None
    
    def get_poke_from_index(self, index):
        for poke in self.pokemons:
            if poke.index == index:
                return poke
        #print("No pokemon has choice_index of %d" % choice_index)

class Pokemon:    
    name = None
    
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
    
    index = None
    curr_index = None

    def __init__(self, request_dict):
        self.name = request_dict['ident'].split(' ')[1]

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
            health_str, cond_str = condition_str.split(' ')
            self.curr_health = int(health_str.split('/')[0])

            # TODO: Handle condition
            #print("Condition: %s" % cond_str)
        else:
            self.curr_health = int(condition_str.split('/')[0])

        self.ability = request_dict['ability']
        self.item = request_dict['item']
        self.active = request_dict['active']
    
    def is_switch_allowed(self):
        return not self.is_fainted() and not self.is_active()
    
    def is_fainted(self):
        return self.curr_health == 0
    
    def is_active(self):
        return self.active
