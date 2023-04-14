from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By

option = webdriver.ChromeOptions()

option.binary_location = r'/Applications/Brave Browser.app/Contents/MacOS/Brave Browser'
driverService = Service('/opt/homebrew/bin/chromedriver')

driver = webdriver.Chrome(service=driverService, options=option)

driver.get("https://search.dreb.es/?q=ping")
pong = driver.find_element(By.XPATH, '/html/body/pre')

print(pong.text)
