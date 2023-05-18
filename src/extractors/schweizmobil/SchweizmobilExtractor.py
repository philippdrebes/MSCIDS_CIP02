from time import sleep

import pandas as pd
import mariadb
from selenium import webdriver
from selenium.webdriver.common.by import By


# Extracting route data from the website schweizmobil.ch
def extract():
    driver = webdriver.Chrome()
    driver.implicitly_wait(30)

    routes = []

    # Local routes
    driver.get('https://schweizmobil.ch/de/wanderland/lokale-routen')

    # Scrolling down to load all routes
    for i in range(1, 150):
        driver.execute_script(f"document.getElementById('main').scrollTop = {i * 500};")
        sleep(1)

    # Extracting route URLs and names
    box = driver.find_elements(By.CSS_SELECTOR, 'a[data-cy="route-card-it"]')
    for b in box:
        url = b.get_attribute('href')
        name = b.find_element(By.CSS_SELECTOR, 'p[data-cy="route-title"]').text
        routes.append({'url': url, 'name': name})

    # Regional routes
    driver.get('https://schweizmobil.ch/de/wanderland/regionale-routen')

    # Scrolling down to load all routes
    for i in range(1, 40):
        driver.execute_script(f"document.getElementById('main').scrollTop = {i * 500};")
        sleep(1)

    regionale_routen = []
    box = driver.find_elements(By.CSS_SELECTOR, 'a[data-cy="route-card-it"]')
    for b in box:
        url = b.get_attribute('href')
        name = b.find_element(By.CSS_SELECTOR, 'p[data-cy="route-title"]').text
        regionale_routen.append({'url': url, 'name': name})

    # Extracting sub-routes for regional routes
    for rr in regionale_routen:
        driver.get(rr['url'])

        etappen = driver.find_elements(By.CSS_SELECTOR, 'a[data-cy="route-list-it"]')
        for etappe in etappen:
            etappe_url = etappe.get_attribute('href')
            etappe_name = etappe.find_element(By.CSS_SELECTOR, 'p[data-cy="route-title"]').text

            routes.append({'url': etappe_url, 'name': f"{rr['name']} {etappe_name}"})

    # National routes
    driver.get('https://schweizmobil.ch/de/wanderland/nationale-routen')

    # Scrolling down to load all routes
    for i in range(1, 5):
        driver.execute_script(f"document.getElementById('main').scrollTop = {i * 500};")
        sleep(1)

    nationale_routen = []
    box = driver.find_elements(By.CSS_SELECTOR, 'a[data-cy="route-card-it"]')
    for b in box:
        url = b.get_attribute('href')
        name = b.find_element(By.CSS_SELECTOR, 'p[data-cy="route-title"]').text
        nationale_routen.append({'url': url, 'name': name})

    # Extracting sub-routes for national routes
    for nr in nationale_routen:
        driver.get(nr['url'])

        # Find all elements with the specified CSS selector
        etappen = driver.find_elements(By.CSS_SELECTOR, 'a[data-cy="route-list-it"]')
        for etappe in etappen:
            etappe_url = etappe.get_attribute('href')
            etappe_name = etappe.find_element(By.CSS_SELECTOR, 'p[data-cy="route-title"]').text

            # Append the sub-route URL and name to the 'routes' list
            routes.append({'url': etappe_url, 'name': f"{nr['name']} {etappe_name}"})

    # This loop iterates over each route in the routes list.
    # For each iteration, it retrieves the URL of the route from the current route dictionary and instructs the web driver to navigate to that URL using driver.get().
    # It then prints the URL using print(route['url']).
    for route in routes:
        driver.get(route['url'])
        print(route['url'])

        # Extract route details such as distance, altitude up, altitude down, and more
        route['distance'] = driver.find_element(By.XPATH,
                                                '//*[@id="main"]/div[2]/page-segment/div[2]/div[4]/div[2]/element-facts/div[1]/div[2]/div/span').text
        route['altitude_up'] = driver.find_element(By.XPATH,
                                                   '//*[@id="main"]/div[2]/page-segment/div[2]/div[4]/div[2]/element-facts/div[1]/div[3]/span').text
        route['altitude_down'] = driver.find_element(By.XPATH,
                                                     '//*[@id="main"]/div[2]/page-segment/div[2]/div[4]/div[2]/element-facts/div[1]/div[4]/span').text

        group2 = driver.find_element(By.XPATH,
                                     '//*[@id="main"]/div[2]/page-segment/div[2]/div[4]/div[2]/element-facts/div[2]')
        items = group2.find_elements(By.CLASS_NAME, 'items-stretch')

        # Check the number of items in the group
        if len(items) == 2:
            # If there are two items, extract difficulty level and fitness level
            route['difficulty_level'] = driver.find_element(By.XPATH,
                                                            '//*[@id="main"]/div[2]/page-segment/div[2]/div[4]/div[2]/element-facts/div[2]/div[2]/span').text
            route['fitness_level'] = driver.find_element(By.XPATH,
                                                         '//*[@id="main"]/div[2]/page-segment/div[2]/div[4]/div[2]/element-facts/div[2]/div[3]/span').text

        if len(items) == 3:
            # If there are three items, extract duration, difficulty level, and fitness level
            route['duration'] = driver.find_element(By.XPATH,
                                                    '//*[@id="main"]/div[2]/page-segment/div[2]/div[4]/div[2]/element-facts/div[2]/div[2]/span').text
            route['difficulty_level'] = driver.find_element(By.XPATH,
                                                            '//*[@id="main"]/div[2]/page-segment/div[2]/div[4]/div[2]/element-facts/div[2]/div[3]/span').text
            route['fitness_level'] = driver.find_element(By.XPATH,
                                                         '//*[@id="main"]/div[2]/page-segment/div[2]/div[4]/div[2]/element-facts/div[2]/div[4]/span').text

    # Create a pandas DataFrame from the 'routes' list and save it to a CSV file
    df = pd.DataFrame(routes)
    df.to_csv('schweizmobil_stage_1.csv', index=False)


# Transforming the extracted data by cleaning and formatting it
def transform():
    df = pd.read_csv('schweizmobil_stage_1.csv')
    df['distance'] = df.apply(lambda row: row.distance.replace(' km', ''), axis=1)
    df['altitude_up'] = df.apply(lambda row: row.altitude_up.replace(' m', '').replace('’', ''), axis=1)
    df['altitude_down'] = df.apply(lambda row: row.altitude_down.replace(' m', '').replace('’', ''), axis=1)
    df['difficulty_level'] = df.apply(
        lambda row: row.difficulty_level.replace(' (Wanderweg)', '').replace(' (Bergwanderweg)', ''), axis=1)

    df['duration'] = df.apply(lambda row: clean_duration(row), axis=1)

    df.to_csv('schweizmobil_stage_3.csv', index=False)


# Cleaning the duration value and convert it to minutes
def clean_duration(row):
    if type(row.duration) is not str:
        return None

    # 2 h 49 min
    values = row.duration.split(' ')

    # ['2', 'h', '49', 'min']
    hours = values[0]

    # Calculating the duration of a route in minutes.
    # It first checks if the values list, which contains the duration components, has a length greater than 2.
    if len(values) > 2:
        minutes = values[2]
        return int(hours) * 60 + int(minutes)
    else:
        return int(hours) * 60


# Loading the transformed data into a database table
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
