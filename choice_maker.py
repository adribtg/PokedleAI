import pandas as pd


class ChoiceMaker():

    def __init__(self):
        self.pokedatabase = pd.read_csv("all_g.csv").fillna("None").astype('str')
        self.pokedatabase['Gen'] = self.pokedatabase['Gen'].apply(int)
        self.pokedatabase['Couleur'] = self.pokedatabase['Couleur'].apply(lambda x : [ele.strip() for ele in x.split(',')])
        self.pokedatabase['Habitat'] = self.pokedatabase['Habitat'].apply(lambda x : [ele.strip() for ele in x.split(',')])
        self.possible_pokemon : pd.DataFrame = self.pokedatabase.copy(deep=True)
    
    def make_guess(self,guess_list):
        for guess in guess_list:
            remaining = self.possible_pokemon.shape[0]
            self.possible_pokemon = self.process_guess(guess)
        remaining = self.possible_pokemon.shape[0]
        print(f"Pokemon restants : {remaining}")
        print(list(self.possible_pokemon["Pokemon"].values))
        pokemon_guessed = self.possible_pokemon.sample(1)["Pokemon"].values[0]
        print(f"Pokémon choisi : {pokemon_guessed}")
        return pokemon_guessed


    def process_guess(self, guess : dict):
        bool_keys = ['Type 1', 'Type 2', "Stade d'évolution",'Entièrement évolué']
        for column in bool_keys:
            self.possible_pokemon = self.filter_bool_key(column,guess)
        self.possible_pokemon = self.filter_gen(guess)
        self.possible_pokemon = self.filter_color(guess)
        self.possible_pokemon = self.filter_habitat(guess)
        return self.possible_pokemon


    def filter_bool_key(self, key : str, guess : dict):
        guess_key = guess.get(key, {})
        for value,bool in guess_key.items():
            if bool=='correct':
                self.possible_pokemon = self.possible_pokemon[self.possible_pokemon[key]==value]
            elif bool=='wrong':
                self.possible_pokemon = self.possible_pokemon[self.possible_pokemon[key]!=value]
                if key=="Type 1":
                    self.possible_pokemon = self.possible_pokemon[self.possible_pokemon["Type 2"]!=value]
                elif key== "Type 2":
                    self.possible_pokemon = self.possible_pokemon[self.possible_pokemon["Type 1"]!=value]
            elif bool=='partial':
                self.possible_pokemon = self.possible_pokemon[self.possible_pokemon["Type 1"]==value] if key=="Type 2" else self.possible_pokemon[self.possible_pokemon["Type 2"]==value]
        
        return self.possible_pokemon
    

    def filter_color(self, guess: dict):
        guess_data = guess.get("Couleur", {})    
        key = "Couleur"
        for colors_tuple, status in guess_data.items():
            proposed_colors = set(colors_tuple) 
            if status == 'correct':
                self.possible_pokemon = self.possible_pokemon[
                    self.possible_pokemon[key].apply(lambda x: set(x) == proposed_colors)
                ]
            elif status == 'partial':
                self.possible_pokemon = self.possible_pokemon[
                    self.possible_pokemon[key].apply(lambda x: 
                        len(proposed_colors.intersection(set(x))) > 0 and set(x) != proposed_colors
                    )
                ]
            elif status == 'wrong':
                self.possible_pokemon = self.possible_pokemon[
                    self.possible_pokemon[key].apply(lambda x: 
                        len(proposed_colors.intersection(set(x))) == 0
                    )
                ]
        return self.possible_pokemon
    
    def filter_habitat(self, guess: dict):
        guess_habitat = guess.get("Habitat", {})       
        key = "Habitat"
        for value, status in guess_habitat.items():
            proposed = {value} if isinstance(value, str) else set(value)
            if status == 'correct':
                self.possible_pokemon = self.possible_pokemon[
                    self.possible_pokemon[key].apply(lambda x: proposed.issubset(set(x)))
                ]
            elif status == 'wrong':
                self.possible_pokemon = self.possible_pokemon[
                    self.possible_pokemon[key].apply(lambda x: not proposed.intersection(set(x)))
                ]
            elif status == 'partial':
                self.possible_pokemon = self.possible_pokemon[
                    self.possible_pokemon[key].apply(
                        lambda x: proposed.issubset(set(x)) and len(set(x)) > len(proposed)
                    )
                ]
        return self.possible_pokemon


    def filter_gen(self,guess):
        gen_guessed = list(guess.get('Gen', {}).keys())[0]
        value = guess.get('Gen',{}).get(gen_guessed)
        if value=='equal':
            return self.possible_pokemon[self.possible_pokemon['Gen']==gen_guessed]
        
        return self.possible_pokemon[self.possible_pokemon['Gen']>gen_guessed] if value=='more' else self.possible_pokemon[self.possible_pokemon['Gen']<gen_guessed]
