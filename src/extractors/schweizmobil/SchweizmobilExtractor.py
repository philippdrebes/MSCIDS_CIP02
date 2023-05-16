from time import sleep

import pandas as pd
import mariadb
from selenium import webdriver
from selenium.webdriver.common.by import By


def extract():
    driver = webdriver.Chrome()
    driver.implicitly_wait(30)

    routes = []

    # lokale routen
    driver.get('https://schweizmobil.ch/de/wanderland/lokale-routen')

    for i in range(1, 150):
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

    # nationale routen
    driver.get('https://schweizmobil.ch/de/wanderland/nationale-routen')

    for i in range(1, 5):
        driver.execute_script(f"document.getElementById('main').scrollTop = {i * 500};")
        sleep(1)

    nationale_routen = []
    box = driver.find_elements(By.CSS_SELECTOR, 'a[data-cy="route-card-it"]')
    for b in box:
        url = b.get_attribute('href')
        name = b.find_element(By.CSS_SELECTOR, 'p[data-cy="route-title"]').text
        nationale_routen.append({'url': url, 'name': name})

    for nr in nationale_routen:
        driver.get(nr['url'])

        etappen = driver.find_elements(By.CSS_SELECTOR, 'a[data-cy="route-list-it"]')
        for etappe in etappen:
            etappe_url = etappe.get_attribute('href')
            etappe_name = etappe.find_element(By.CSS_SELECTOR, 'p[data-cy="route-title"]').text

            routes.append({'url': etappe_url, 'name': f"{nr['name']} {etappe_name}"})

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


def transform():
    df = pd.read_csv('schweizmobil_stage_1.csv')
    df['distance'] = df.apply(lambda row: row.distance.replace(' km', ''), axis=1)
    df['altitude_up'] = df.apply(lambda row: row.altitude_up.replace(' m', '').replace('’', ''), axis=1)
    df['altitude_down'] = df.apply(lambda row: row.altitude_down.replace(' m', '').replace('’', ''), axis=1)
    df['difficulty_level'] = df.apply(
        lambda row: row.difficulty_level.replace(' (Wanderweg)', '')
        .replace(' (Bergwanderweg)', '')
        .replace(' ( Bergwanderweg)', '')
        .replace(' (Wanderweg; Lägerengrat: Bergwanderweg)', ''), axis=1)

    df['duration'] = df.apply(lambda row: clean_duration(row), axis=1)

    df.to_csv('schweizmobil_stage_3.csv', index=False)


def clean_duration(row):
    if type(row.duration) is not str:
        return None

    # 2 h 49 min
    values = row.duration.split(' ')

    # ['2', 'h', '49', 'min']
    hours = values[0]

    if len(values) > 2:
        minutes = values[2]
        return int(hours) * 60 + int(minutes)
    else:
        return int(hours) * 60


def load():
    df = pd.read_csv('schweizmobil_stage_3.csv')

    # connection parameters
    conn_params = {
        "user": "root",
        "password": "my-secret-pw",
        "host": "127.0.0.1",
        "database": "cip"
    }

    # Establish a connection
    connection = mariadb.connect(**conn_params)
    cursor = connection.cursor()

    sql = "INSERT INTO schweizmobil (url,name,distance,altitude_up,altitude_down,duration,difficulty_level,fitness_level) " \
          "VALUES (?,?,?,?,?,?,?,?)"
    data = []

    for index, row in df.iterrows():
        data.append(
            (row['url'], row['name'], row['distance'], row['altitude_up'], row['altitude_down'], row['duration'],
             row['difficulty_level'], row['fitness_level'])
        )

    # insert data
    cursor.executemany(sql, data)
    connection.commit()

    # free resources
    cursor.close()
    connection.close()


if __name__ == '__main__':
    extract()
    transform()
    load()
