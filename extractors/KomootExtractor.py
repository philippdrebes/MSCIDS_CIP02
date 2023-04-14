from selenium.webdriver.common.by import By

from extractors.BaseExtractor import BaseExtractor
import extractors.Selenium


class KomootExtractor(BaseExtractor):

    base_url = 'https://www.komoot.com/discover/hiking-trails'

    def __init__(self):
        super().__init__("Komoot")

    def extract(self):
        super().extract()

        driver = extractors.Selenium.initialize_new_instance()

        driver.get("https://search.dreb.es/?q=ping")
        pong = driver.find_element(By.XPATH, '/html/body/pre')

        print(pong.text)

