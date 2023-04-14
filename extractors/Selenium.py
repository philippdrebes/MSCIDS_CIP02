import platform
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.webdriver import WebDriver


def initialize_new_instance() -> WebDriver:
    plt = platform.system()
    if plt == 'Darwin':
        option = webdriver.ChromeOptions()
        option.binary_location = r'/Applications/Brave Browser.app/Contents/MacOS/Brave Browser'
        driver_service = Service('/opt/homebrew/bin/chromedriver')

        driver = webdriver.Chrome(service=driver_service, options=option)
        return driver

    driver = webdriver.Chrome()
    return driver
