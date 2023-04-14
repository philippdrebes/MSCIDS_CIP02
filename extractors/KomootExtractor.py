from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from extractors.BaseExtractor import BaseExtractor


class KomootExtractor(BaseExtractor):

    base_url = 'https://www.komoot.com/discover/hiking-trails'

    def __init__(self):
        super().__init__("Komoot")

    def extract(self):
        super().extract()
        option = webdriver.ChromeOptions()

        option.binary_location = r'/Applications/Brave Browser.app/Contents/MacOS/Brave Browser'
        driverService = Service('/opt/homebrew/bin/chromedriver')

        driver = webdriver.Chrome(service=driverService, options=option)

        driver.get("https://search.dreb.es/?q=ping")
        pong = driver.find_element(By.XPATH, '/html/body/pre')

        print(pong.text)

