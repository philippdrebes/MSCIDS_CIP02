

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import pandas as pd


###########################################################################
# Set up Keyring in GitHub
# - Ask for Username and Password if not already saved in the OS keyring
# - Store the new Credentials in the Keystore

import keyring
import getpass

keyringServiceNAme = "SAC Weblogin"

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
url = 'https://www.sac-cas.ch/en/login/?redirect_url=%2Fen%2Fhuts-and-tours%2Fsac-route-portal%2F&cHash=61fe243516fab7669ff192457a7ef6c5'
driver.get(url)
driver.implicitly_wait(1)

# Login
driver.find_element(by=By.XPATH, value='//input[@name="username"]').send_keys(credentials.username)
driver.find_element(by=By.XPATH, value='//input[@name="password"]').send_keys(credentials.password)
driver.find_element(by=By.XPATH, value='//button[@type="submit"]').click()

# Dismiss Cookie
driver.implicitly_wait(2)
driver.find_element(by=By.XPATH, value='//button[@id="CybotCookiebotDialogBodyButtonDecline"]').click()

# Select mountain_hiking icon
driver.implicitly_wait(5)
driver.find_element(by=By.XPATH, value='//form[@class="m-destination-filter__form"]/ul/li[2]/label/div').click()

# Finding destination number on website
driver.implicitly_wait(15)
destinations = driver.find_element(by=By.XPATH, value='//span[@class="m-destination-list__count-label fs-copy"]').text

# Filter out destination number
print(destinations)
dest_num = ""
for c in destinations:
    if c.isdigit():
        dest_num = dest_num + c
print("Extracted numbers from the list : " + dest_num)

#TO DO remove for TEST
dest_num = 1

# Click on "show more button" to open up all destination subpages
for i in range(1,int(dest_num)):
    try:
        driver.find_element(by=By.XPATH, value='//button[@class="m-teaser-list__more c-button c-button--secondary"]').click()
        driver.implicitly_wait(1)
    except:
        break
    print("i: ", i)

##########################################################################
# Get tour_page link attributes from all huts and mountain_hike pages and save it a tour_list:

# Collect all webelements of the huts & hikes subpages:
huts_hikes = driver.find_elements(by=By.XPATH, value='.//a[@class="c-teaser-destination__link"]') #option:by Xpath
#huts_hikes = driver.find_elements(by=By.CLASS_NAME, value="c-teaser-destination__link") #option:by class

huts_hikes_link_list=[]
tour_link_list=[]

# Get links from selenium webelements huts & hikes
for item1 in huts_hikes:
    href_huts_hikes = item1.get_attribute('href')
    huts_hikes_link_list.append(href_huts_hikes)

print("We have got ", len(huts_hikes_link_list), " huts and hike page links and visit now each of them.")

# Open subpages and save tour_page links in the tour_link_list.
# These tour pages will be our target pages to crawl information from:
for item2 in huts_hikes_link_list:
    driver.get(item2) # Open tour pages
    tour_page = driver.find_elements(by=By.XPATH, value='.//*[@id="poi"]/div/nav[1]/table/tbody/tr/td[1]/a')
    for tp in tour_page:
        try: # Extract tour_page links from webelement
            href_tour_page = tp.get_attribute('href')
            if href_tour_page not in tour_link_list: # Check of duplicates / only saving unique tour links
                tour_link_list.append(href_tour_page)
            else:
                continue
        except:
            print("item3: no href attribute") # Releasing error, in case no tour page on the huts & hikes page

# Summary of our link list & number of target pages:
print("We have crawled ",len(tour_link_list)," tour_page links:" )
#print(tour_link_list)

# Save the tour_link_list to a separate csv file
# (useful in case of we have error messages in crawilng the data in the next step, we can run through this csv):
link_data =[]
for link in tour_link_list:
    link_dict = {
        'link': link}
    link_data.append(link_dict)

df_tour_page_links = pd.DataFrame(link_data)
print(df_tour_page_links.head(10))

# Export the DataFrame to a CSV file
df_tour_page_links.to_csv("SAC_page_links.csv",sep=';')

print("Now we will crawl the information from all of them.")

##############################################################################
#Tour_list contains all tour subsite links, which we are crawling below:
tour_data=[]
i=0
for tour_page in tour_link_list:
    driver.get(tour_page)
    # Header from which we generate the title and subtitle data:
    try:
        header = driver.find_element(by=By.XPATH, value='/html/body/div[4]/div[5]/div[1]/div[2]/h2').text
        title = header.split("\n")[0]
        subtitle = header.split("\n")[1]
    except:
        header ="na"
        title = "na"
        subtitle = "na"
    # Difficulty level in scale of T1 - T6:
    try:
        difficulty = driver.find_element(by=By.XPATH, value='.//*[@id="route"]/div[3]/ul/li[1]/dl/dd/a').text
    except:
        difficulty = "na"
    # Ascent, descent and time we do not have at all pages - we fill missing values with na:
    try:
        route_info_a = driver.find_element(by=By.XPATH, value='.//*[@id="route"]/div[3]/ul/li[2]/dl/dd').text
        time_a = route_info_a.split(",")[0]
        ascent = route_info_a.split(",")[1]
    except:
        route_info_a = "na"
        time_a = "na"
        ascent = "na"
    try:
        route_info_d = driver.find_element(by=By.XPATH, value='.//*[@id="route"]/div[3]/ul/li[3]/dl/dd').text
        time_d = route_info_d.split(",")[0]
        descent = route_info_d.split(",")[1]
    except:
        route_info_d = "na"
        time_d = "na"
        descent ="na"
    # Map link which is unique for each tour page:
    try:
        map = driver.find_elements(by=By.XPATH, value='.//*[@hreflang="x-default"]')
        map_link =""
        for mp in map:
            map_link = mp.get_attribute('href')
    except:
        map ="na"
    # Description is located in an accordion in html, has different number of rows at each subpage
    # we extract only first row of description with CSS selector, we do not extract the different variants of the tours:
    try:
        description = driver.find_element(By.CSS_SELECTOR,'*>div.m-route-accordion__description.c-rich-text>p').text
    except:
        description = "na"
    tour_dict_item = {
        'title': title,
        'subtitle': subtitle,
        'difficulty': difficulty,
        'time_ascent': time_a,
        'ascent': ascent,
        'time_descent': time_d,
        'descent': descent,
        'link': tour_page,
        'map': map_link,
        'description': description}
    tour_data.append(tour_dict_item)
    if i%10 == 0:
        print("Get infos of ", i ,"/", len(tour_link_list), " hiking tours.")
    i+=1

###########################################################################
# Creating and printing a data frame
df = pd.DataFrame(tour_data)
print(df.head(10))

# Export the DataFrame to a CSV file, we create 2 files:
# 1. saves the data in the same file / overwrites database (indexing is included)
df.to_csv("SAC_data_with_index1.csv",sep=';')

# 2. saves the data in the same file / overwrites database (indexing is disabled) -> we can append it later
df.to_csv("SAC_data_without_index1.csv",sep=';',index = False)

# 3. appends an existing csv file with new data:
#df.to_csv("SAC_data_without_index.cs",sep=';', mode ="a", header = False, index = False)

# Closing browser
driver.quit()    # the selenium-controlled chrome browser is terminated
#driver.close()    # the you don't see the result

print("end SacExtractor.py")
print("end")
