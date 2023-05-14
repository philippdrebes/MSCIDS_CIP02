from time import sleep

import pandas as pd
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.webdriver import WebDriver
from selenium.webdriver.common.by import By

from src.extractors import SeleniumUtil


def main():
    driver = webdriver.Chrome()
    driver.implicitly_wait(15)

    routes = []

    # lokale routen
    driver.get('https://schweizmobil.ch/de/wanderland/lokale-routen')

    for i in range(1, 100):
        driver.execute_script(f"document.getElementById('main').scrollTop = {i * 500};")
        sleep(1)

    box = driver.find_elements(By.CSS_SELECTOR, 'a[data-cy="route-card-it"]')
    for b in box:
        url = b.get_attribute('href')
        name = b.find_element(By.CSS_SELECTOR, 'p[data-cy="route-title"]').text
        routes.append({'url': url, 'name': name})

    # regionale routen
    driver.get('https://schweizmobil.ch/de/wanderland/regionale-routen')

    for i in range(1, 40):
        driver.execute_script(f"document.getElementById('main').scrollTop = {i * 500};")
        sleep(1)

    regionale_routen = []
    box = driver.find_elements(By.CSS_SELECTOR, 'a[data-cy="route-card-it"]')
    for b in box:
        url = b.get_attribute('href')
        name = b.find_element(By.CSS_SELECTOR, 'p[data-cy="route-title"]').text
        regionale_routen.append({'url': url, 'name': name})

    for rr in regionale_routen:
        driver.get(rr['url'])

        etappen = driver.find_elements(By.CSS_SELECTOR, 'a[data-cy="route-list-it"]')
        for etappe in etappen:
            etappe_url = etappe.get_attribute('href')
            etappe_name = etappe.find_element(By.CSS_SELECTOR, 'p[data-cy="route-title"]').text

            routes.append({'url': etappe_url, 'name': f"{rr['name']} {etappe_name}"})

    for route in routes:
        driver.get(route['url'])
        print(route['url'])
        route['distance'] = driver.find_element(By.XPATH,
                                                '//*[@id="main"]/div[2]/page-segment/div[2]/div[4]/div[2]/element-facts/div[1]/div[2]/div/span').text
        route['altitude_up'] = driver.find_element(By.XPATH,
                                                   '//*[@id="main"]/div[2]/page-segment/div[2]/div[4]/div[2]/element-facts/div[1]/div[3]/span').text
        route['altitude_down'] = driver.find_element(By.XPATH,
                                                     '//*[@id="main"]/div[2]/page-segment/div[2]/div[4]/div[2]/element-facts/div[1]/div[4]/span').text

        group2 = driver.find_element(By.XPATH,
                                     '//*[@id="main"]/div[2]/page-segment/div[2]/div[4]/div[2]/element-facts/div[2]')
        items = group2.find_elements(By.CLASS_NAME, 'items-stretch')

        if len(items) == 2:
            route['difficulty_level'] = driver.find_element(By.XPATH,
                                                            '//*[@id="main"]/div[2]/page-segment/div[2]/div[4]/div[2]/element-facts/div[2]/div[2]/span').text
            route['fitness_level'] = driver.find_element(By.XPATH,
                                                         '//*[@id="main"]/div[2]/page-segment/div[2]/div[4]/div[2]/element-facts/div[2]/div[3]/span').text

        if len(items) == 3:
            route['duration'] = driver.find_element(By.XPATH,
                                                    '//*[@id="main"]/div[2]/page-segment/div[2]/div[4]/div[2]/element-facts/div[2]/div[2]/span').text
            route['difficulty_level'] = driver.find_element(By.XPATH,
                                                            '//*[@id="main"]/div[2]/page-segment/div[2]/div[4]/div[2]/element-facts/div[2]/div[3]/span').text
            route['fitness_level'] = driver.find_element(By.XPATH,
                                                         '//*[@id="main"]/div[2]/page-segment/div[2]/div[4]/div[2]/element-facts/div[2]/div[4]/span').text

    df = pd.DataFrame(routes)
    df.to_csv('schweizmobil_stage_1.csv', index=False)


if __name__ == '__main__':
    main()
