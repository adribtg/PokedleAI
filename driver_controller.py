from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from webdriver_manager.firefox import GeckoDriverManager
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
import time

class DriverController:

    def __init__(self,battle_link):
        
        service = Service(GeckoDriverManager().install())
        self.driver = webdriver.Firefox(service=service)
        self.battle_link = battle_link
        self.wait = WebDriverWait(self.driver, 10)
        self.driver.get(self.battle_link)

        try:
            cookie_btn = self.wait.until(
                EC.element_to_be_clickable((By.XPATH, "//button[contains(., 'Consent')]"))
            )
            cookie_btn.click()
        except:
            pass

    
    def wait_my_turn(self):
        print("En attente de mon tour ou d'une revanche...")
        
        while True:
            try:
                turn_elements = self.driver.find_elements(By.XPATH, '//div[contains(@class,"card")]//div[contains(text(),"Votre tour")]')
                if len(turn_elements) > 0 and turn_elements[0].is_displayed():
                    print("C'est mon tour !")
                    return "turn"

                rematch_button = self.driver.find_elements(By.XPATH, '//button[contains(@class,"btn-green") and text()="ACCEPTER"]')
                if len(rematch_button) > 0 and rematch_button[0].is_displayed():
                    print("Demande de revanche détectée...")
                    rematch_button[0].click()
                    time.sleep(1)
                    return "reset"

            except Exception as e:
                print(f"Erreur mineure durant l'attente : {e}")
            time.sleep(0.5)



    def make_guess(self,pokemon):
        try:
            input_box = self.wait.until( 
                EC.element_to_be_clickable((By.CSS_SELECTOR, "input[type='text']")) 
                ) 
        except:
            self.wait_my_turn()
            return
        
        input_box.clear() 
        input_box.send_keys(pokemon) 
        input_box.send_keys(Keys.ENTER)


    def get_rows(self):
        try:
            rows = self.driver.find_elements(
                By.XPATH,
                '//div[contains(@class, "flex") and contains(@class, "w-fit") and contains(@class, "justify-center")]'
            )
            return rows[1:]
        except Exception as e:
            print(f"Erreur lors de la récupération des lignes: {e}")
            return []


    def parse_row(self,row,retry=False):
        try:
            cards = row.find_elements(
        By.XPATH,
        './/div[contains(@class, "result-card") and not(ancestor::div[contains(@style,"rotateY(180deg)")])]'
    )

            return {
                "Pokemon": self.get_card_imgs(cards[0])[0].get_attribute("title"),
                "Type 1": self.read_type(cards[2]),
                "Type 2": self.read_type(cards[4]),
                "Stade d'évolution" : self.read_type(cards[6]),
                "Entièrement évolué" : self.read_type(cards[8]),
                "Couleur": self.read_colors(cards[10]),
                "Habitat": self.read_habitat(row),
                "Gen": self.read_gen(cards[14]),
            }
        except:
            if not retry:
                time.sleep(1)
                self.parse_row(row,retry=True)
            else:
                print("Impossible de parser la ligne : ",row)


    def read_type(self,card):
        text = self.get_card_text(card)
        color = self.get_card_color(card)

        if not text:
            return None

        return {text: color}
    
    def read_gen(self, card):
        text = card.find_element(By.XPATH, ".//div[contains(@class, 'absolute')]").text.strip().lower()
        imgs = self.get_card_imgs(card)

        if not text:
            return None

        direction = "equal"

        for img in imgs:
            alt = img.get_attribute("alt")
            if not alt:
                continue

            alt = alt.lower()

            if "arrow-down" in alt:
                direction = "more"
            elif "arrow-up" in alt:
                direction = "less"

        return {int(text): direction}
    
    def read_habitat(self, row):
        try:
            # 1. récupérer les barres de couleur (en haut)
            bars = row.find_elements(
                By.XPATH,
                './/div[contains(@class,"xl:pixel-corners")]//div[contains(@style,"background-color")]'
            )

            states = [self.get_card_color(bar) for bar in bars]

            # 2. récupérer les images d’habitat
            imgs = row.find_elements(By.XPATH, './/img[@alt]')

            habitats = []
            for img in imgs:
                alt = img.get_attribute("alt")
                if alt and alt not in ["pokemon sprite", "poke ball card back"]:
                    habitats.append(alt.lower())

            # 3. associer
            result = {}
            for i in range(min(len(habitats), len(states))):
                result[habitats[i]] = states[i]

            return result if result else None

        except:
            return None
    

    def read_bool(self,card):
        text = self.get_card_text(card)
        if not text:
            return None

        return {text: text == "oui"}


    def read_colors(self, card):
        text = self.get_card_text(card)
        if not text:
            return None

        state = self.get_card_color(card)

        return {tuple(sorted(text.strip().replace(',',';').replace(' ','').split(';'))): state}

    #Helpers
    def get_card_color(self, card):
        try:
            style = card.get_attribute("style") or ""

            if "rgb(70, 217, 48)" in style:
                return "correct"
            elif "rgb(237, 59, 43)" in style:
                return "wrong"
            elif "rgb(237, 159, 43)" in style:
                return "partial"

        except:
            pass

        return "unknown"


    def get_card_text(self,card):
        try:
            return card.find_element(By.TAG_NAME, "p").text.strip()
        except:
            return None


    def get_card_imgs(self,card):
        return card.find_elements(By.TAG_NAME, "img")