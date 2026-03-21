import argparse
from driver_controller import DriverController
from choice_maker import ChoiceMaker
import time
import random

class PokedleAI:

    def init_parser(self):
        parser = argparse.ArgumentParser(description="IA Pokedle")
        parser.add_argument(
            "--battle_link",
            type=str,
            required=True,
            help="Lien du défi"
        )
        parser.add_argument(
            "--difficulte",
            type=int,
            choices=range(1, 6),
            default=5,
            help="Niveau de difficulté : entier entre 1 et 5."
        )

        args = parser.parse_args()
        return args
    

    def run(self):
        self.args = self.init_parser()
        partie = DriverController(battle_link=self.args.battle_link)
        guesser = ChoiceMaker()
        while True:
            waiter = partie.wait_my_turn()
            if waiter=='reset':
                guesser = ChoiceMaker()
            time.sleep(random.randint(3000,5000)/1000)
            lignes = partie.get_rows()
            guesses = [partie.parse_row(guess) for guess in lignes]
            pokemon = guesser.make_guess(guesses)        
            partie.make_guess(pokemon)
            time.sleep(random.randint(3000,5000)/1000)
   
        

if __name__ == "__main__":
    PokedleAI().run()
