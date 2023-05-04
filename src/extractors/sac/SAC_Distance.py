
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
import pandas as pd
import os
import re

###########################################################################
# Set up Keyring in GitHub
# - Ask for Username and Password if not already saved in the OS keyring
# - Store the new Credentials in the Keystore

import keyring
import getpass

keyringServiceNAme = "SchweizMobil Weblogin"

while True:
    credentials = keyring.get_credential(keyringServiceNAme, None)
    if credentials == None:
        try:
            username = input('Please enter SAC Username: ')
        except Exception as error:
            print('USERNAME READ ERROR', error)
        try:
            password = getpass.getpass(prompt='Please enter SAC Password: ')
        except Exception as error:
            print('PASSWORD READ ERROR', error)
        try:
            keyring.set_password(keyringServiceNAme, username, password)
        except Exception as error:
            print('PASSWORD SAVE ERROR', error)
    else: # we have a username and password
        break
#print("Scrapping with user: " + credentials.username)
#print("and password: "+ credentials.password)

###########################################################################


# Get to the target page sign in and filter# Set up webdriver
print("start")
driver = webdriver.Chrome()

# Open URL
url = 'https://map.schweizmobil.ch/?lang=en&showLogin'
driver.get(url)
driver.implicitly_wait(10)

# Login
driver.find_element(by=By.XPATH, value='//*[@id="username"]').send_keys(credentials.username)
driver.find_element(by=By.XPATH, value='//*[@id="password"]').send_keys(credentials.password)
driver.find_element(by=By.XPATH, value='//*[@id="mytracks"]/app-tracks/div/div/app-user/form/div[4]/button').click()

# "go to you tour list?" Page
# Wait for complete loading or we are missing the element
wait = WebDriverWait(driver, 10)
element = wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="mytracks"]/app-tracks/div/div/app-user/app-user-welcome/div[3]/a')))

try:
    driver.find_element(by=By.XPATH, value='//*[@id="mytracks"]/app-tracks/div/div/app-user/app-user-welcome/div[3]/a').click()
except:
    # In case the waiting was not working, just try again.
    driver.find_element(by=By.XPATH, value='//*[@id="mytracks"]/app-tracks/div/div/app-user/app-user-welcome/div[3]/a').click()

files =[]
basepath = 'C:\\Users\\A\\switchdrive\\SyncVM\\CIP_FS23\\Project\\GPX\\'
for entry in os.listdir(basepath):
    if os.path.isfile(os.path.join(basepath, entry)):
        files.append(entry)

distance_data=[]

XPATH_IMPORT_GPS_TRACK = '//*[@id="mytracks"]/app-tracks/div/app-track-list/div[2]/div/a'
XPATH_THE_TOUR_COULD_NOT_BE_IMPORTEDD_OK_BUTTON = '/html/body/div[11]/div/div/div[2]/button'
XPATH_GPX_FILE_SELECTION = '//*[@id="gps_import_form"]/div[1]/span[1]/input[2]'
XPATH_GPX_FILE_UPLOAD_IMPORT_BUTTON = '//*[@id="gps_import_form"]/div[2]/button[1]'

for file in files:
    # Click on Button Import GPX File
    try:

        driver.find_element(by=By.XPATH, value=XPATH_IMPORT_GPS_TRACK).click()
    except:
        try:
            driver.find_element(by=By.XPATH, value=XPATH_THE_TOUR_COULD_NOT_BE_IMPORTEDD_OK_BUTTON).click()
            driver.find_element(by=By.XPATH, value=XPATH_IMPORT_GPS_TRACK).click()
        except:
            continue
    #Input GPX file
    # File selection
    driver.find_element(by=By.XPATH, value=XPATH_GPX_FILE_SELECTION).send_keys(basepath + file)
    # Upload
    driver.find_element(by=By.XPATH, value=XPATH_GPX_FILE_UPLOAD_IMPORT_BUTTON).click()

    # Collect data from page
    try:
        id = re.search(r'(\d+)', file).group(1)
        distance = driver.find_element(by=By.XPATH, value='//*[@id="mytracks"]/app-tracks/div/div[1]/app-track-facts/div/div[3]/span[2]').text
        elevation = driver.find_element(by=By.XPATH, value='//*[@id="mytracks"]/app-tracks/div/div[1]/app-track-facts/div/div[9]/span[2]').text
        up = elevation.split('/')[0]
        down = elevation.split('/')[1]
        height = driver.find_element(by=By.XPATH, value='//*[@id="mytracks"]/app-tracks/div/div[1]/app-track-facts/div/div[10]/span[2]').text
        min = height.split('/')[0]
        max = height.split('/')[1]
    except:
        distance = "na"
        elevation = "na"
        up = "na"
        down = "na"
        height = "na"
        min = "na"
        max = "na"

    distance_dict_item = {
        'id': id, # get id from GPX file name
        'distance': distance,
        'up': up,
        'down': down,
        'min': min,
        'max': max}
    distance_data.append(distance_dict_item)
    # click to get back "go to you tour list?" Page
    try:
        wait = WebDriverWait(driver, 10)
        element = wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="mytracks"]/app-tracks/div/div[2]/div[11]/a')))
    except:
        continue
    try:
        driver.find_element(by=By.XPATH, value='//*[@id="mytracks"]/app-tracks/div/div[2]/div[11]/a').click()
    except:
        # In case the waiting was not working, just try again.
        driver.find_element(by=By.XPATH, value='//*[@id="mytracks"]/app-tracks/div/div[2]/div[11]/a').click()
    print("loop end"+ file)
#for loop end


df = pd.DataFrame(distance_data)
print(df.head(10))

# Export the DataFrame to a CSV file, we create 2 files:
# 1. saves the data in the same file / overwrites database (indexing is included)
df.to_csv("Distance_data_with_index.csv",sep=';')

# 2. saves the data in the same file / overwrites database (indexing is disabled) -> we can append it later
df.to_csv("Distance_data_without_index.csv",sep=';',index = False)

# 3. appends an existing csv file with new data:
#df.to_csv("SAC_data_without_index.cs",sep=';', mode ="a", header = False, index = False)

# Closing browser
driver.quit()    # the selenium-controlled chrome browser is terminated
#driver.close()    # the you don't see the result

print("end DistanceExtractor.py")
print("end")
