from datetime import datetime
import re

import pandas as pd

from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By


class Poste:
    def __init__(self):
        self.id = None
        self.localite = None
        self.route = None
        self.direction = None
        self.sens = None
        
    def __repr__(self):
        return f"Poste {self.id}"


class Selector:
    # https://www.selenium.dev/selenium/docs/api/py/webdriver/selenium.webdriver.common.by.html
    BASE_URL = "https://www2.pch.etat.lu/comptage/home.jsf"
    TABLE_POSTES = (By.CSS_SELECTOR, 'table.liste_poste')
    TR = (By.CSS_SELECTOR, 'tbody>tr')
    TD = (By.TAG_NAME, 'td')
    LINKS = (By.TAG_NAME, 'a')
    DATE_START = (By.ID, "j_idt21:dateDuInputDate")
    DATE_STOP = (By.ID, "j_idt21:dateAuInputDate")
    DIRECTION = (By.ID, 'j_idt21:direction')
    TABLE_RESULT = (By.CSS_SELECTOR, 'table.tablepch')
    SUBMIT_BTN = (By.XPATH, "//input[@type='submit']")
    RETURN_BLOCK = (By.ID, "recherche")


class HomePageParser:
    """
    A class for main page locators. All main page locators should come here
    """
    def __init__(self, driver):
        self.driver = driver
        self.wait = WebDriverWait(driver, 5)
        self.postes = []
        
    def open_homepage(self):
        self.driver.get(Selector.BASE_URL)
        self.wait.until(EC.presence_of_element_located(Selector.TABLE_POSTES))
        
    def extract_all_posts(self):
        self.postes = []
        for table in driver.find_elements(*Selector.TABLE_POSTES):
            for row in table.find_elements(*Selector.TR):
                poste = Poste()
                columns = row.find_elements(*Selector.TD)
                poste.id = columns[0].text
                poste.localite = columns[1].text
                poste.route = columns[2].text
                poste.direction = columns[3].text
                self.postes.append(poste)
                
    def open_form_for_post_id(self, id: str):
        elem = self.driver.find_element(By.LINK_TEXT, id)
        elem.click()
        self.wait.until(EC.presence_of_element_located(Selector.DATE_START))

    def close(self):
        self.driver.close()

        
class FormPageParser(object):
    """
    A class for search results locators. All search results locators should come here
    """
    regex = re.compile("\((.*?)\)")
    
    def __init__(self, driver):
        self.driver = driver
        self.wait = WebDriverWait(driver, 5)

    def set_start_date(self, dt: datetime):
        date_start = self.driver.find_element(*Selector.DATE_START)
        date_start.clear()
        date_start.send_keys(dt.strftime("%d.%m.%Y"))

    def set_stop_date(self,  dt: datetime):
        date_stop = self.driver.find_element(*Selector.DATE_STOP)
        date_stop.clear()
        date_stop.send_keys(dt.strftime("%d.%m.%Y"))
        
    def set_direction(self, idx):
        direction_form = self.driver.find_element(*Selector.DIRECTION).find_elements(*Selector.TD)
        direction_input = direction_form[idx]
        direction_text = self.regex.findall(direction_input.text)[0]
        direction_input.click()
        return direction_text
        
    def submit(self):
        submit = self.driver.find_element(*Selector.SUBMIT_BTN)
        submit.click()
        self.wait.until(EC.presence_of_element_located(Selector.TABLE_RESULT))
        
    def is_valid_date_range(self):
        form = self.driver.find_element(*Selector.DIRECTION).find_elements(*Selector.TD)
        return len(form) > 0
    
        
class ResultPageParser(object):
    """
    A class for search results locators. All search results locators shouldcome here
    """    
    def __init__(self, driver):
        self.driver = driver
        self.wait = WebDriverWait(driver, 5)

    def extract(self):
        rows = self.driver.find_element(*Selector.TABLE_RESULT).find_elements(*Selector.TR)
        utilitaires = self._extract_from_row(rows[2]) + self._extract_from_row(rows[8])
        voitures = self._extract_from_row(rows[3]) + self._extract_from_row(rows[9])
        return utilitaires, voitures

    def _extract_from_row(self, row):
        return [int(x.text) for x in row.find_elements(*Selector.TD)] 
    
    def back(self):
        btn = self.driver.find_element(*Selector.RETURN_BLOCK).find_elements(*Selector.LINKS)[1]
        btn.click()
        self.wait.until(EC.presence_of_element_located(Selector.DATE_START))
        
        
def serialize(poste, direction, dt, utilitaires, voitures):
    for i in range(24):
        yield {
            "POSTE_ ID" : poste.id,
            "Date": dt.replace(hour=i),
            "Direction" : direction,
            "Vehicule" : "V",
            "Localite": poste.localite,
            "Route": poste.route,
            "Sens": poste.sens,
            "COMPTAGE": voitures[i]
        }
    for i in range(24):
        yield {
            "POSTE_ ID" : poste.id,
            "Date": dt.replace(hour=i),
            "Direction" : direction,
            "Vehicule" : "U",
            "Localite": poste.localite,
            "Route": poste.route,
            "Sens": poste.sens,
            "COMPTAGE": utilitaires[i]
        }
        
def process(dt):
    data = []
    print("Extract all posts")
    homepage.open_homepage()
    homepage.extract_all_posts()
    
    for poste in homepage.postes:
        print(f"Extraction of poste ID: {poste.id}")
        homepage.open_form_for_post_id(poste.id)
        formpage.set_start_date(dt)
        formpage.set_stop_date(dt)
        driver.implicitly_wait(0.1)  # wait for js to remove the direction if there is no data for this time
        for direction in range(3):
            try: # replace the if formpage.is_valid_date_range()
                poste.sens = formpage.set_direction(direction)
                formpage.submit()
                u, v = resultpage.extract()
                
                data += list(serialize(poste, direction, dt, u, v))
                
                resultpage.back()
            except:
                print(f"No data for poste ID: {poste.id}")
                break
        homepage.open_homepage() # redirect to homepage to process the next poste
    return data


if __name__ == "__main__":
    # https://selenium-python.readthedocs.io/
    
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("-dt", "--date", help="date to extract in format like 21/10/2020 - Missing is yesterday")
    args = parser.parse_args()
    
    if args.date:
        dt = datetime.strptime(args.date, "%d/%m/%Y")
    else:
        yesterday = datetime.now() - timedelta(days=1)
        dt = yesterday.replace(hour=0, minute=0, second=0)
    
    driver = webdriver.Firefox()
    
    homepage = HomePageParser(driver)
    formpage = FormPageParser(driver)
    resultpage = ResultPageParser(driver)
    
    data = process(dt)
    driver.close()
    
    pd.DataFrame(data).to_csv(f"extract_{dt.strftime('%d%m%Y')}.csv", index=False)
    