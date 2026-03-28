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
    
    def smart_sleep(self, seconds, partie):
        stop_time = time.time() + seconds
        while time.time() < stop_time:
            status = partie.wait_my_turn(verbose=False)
            if status != "turn":
                return False
            time.sleep(0.3)
        return True
        

    def run(self):
        self.args = self.init_parser()
        partie = DriverController(battle_link=self.args.battle_link)
        guesser = ChoiceMaker()
        
        while True:
            status = partie.wait_my_turn()
            if status == "waiting":
                time.sleep(1)
                continue
            if status == "reset":
                guesser = ChoiceMaker()
                print("--- Nouveau match : Base de données réinitialisée ---")
                time.sleep(2)
                continue 

            if status == "turn":
                if not self.smart_sleep(random.randint(2, 4), partie):
                    continue 

                lignes = partie.get_rows()
                guesses = [partie.parse_row(guess) for guess in lignes]
                pokemon = guesser.make_guess(guesses)
                if pokemon:
                    partie.make_guess(pokemon)
                    self.smart_sleep(2, partie)
                

    def run_classique(self):
        self.args = self.init_parser()
        partie = DriverController(battle_link=self.args.battle_link)
        guesser = ChoiceMaker()
        while True:
            guesser = ChoiceMaker()
            lignes = partie.get_rows()
            guesses = [partie.parse_row(guess) for guess in lignes]
            pokemon = guesser.make_guess(guesses)
            partie.make_guess(pokemon)
            time.sleep(random.randint(3000,5000)/1000)


if __name__ == "__main__":
    PokedleAI().run()
