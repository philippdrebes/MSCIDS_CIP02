from selenium.webdriver.common.by import By

import extractors.Selenium


class KomootExtractor:
    base_url = 'https://www.komoot.com/discover/hiking-trails'

    page_objects = {
        'discover': {
            'filter_btn': '//*[@id="pageMountNode"]/div/div[3]/div[2]/div/div/main/section[1]/div[2]/div/div[1]/div/div/button[1]',
            'filter_country_ch_lbl': '//*[@id="pageMountNode"]/div/div[3]/div[2]/div/div/main/section[1]/div[2]/div/div[2]/div/div[2]/div/div[13]/label',
            'next_page_btn': '//*[@id="pageMountNode"]/div/div[3]/div[2]/div/div/main/section[1]/div[2]/div/div[3]/div[3]/button',
        },
        'region': {
            'tour_title_attr': 'data-test-id="tour_title"',
        },
        'tour': {
            'title_lbl': '//*[@id="title"]/div[2]/h1',
            'difficulty_lbl': '//*[@id="pageMountNode"]/div/div[3]/div[2]/div/div/div/div/div[1]/div/div/div/div[2]/div/div[2]/div/div[1]/div/div',
            'duration_lbl': '//*[@id="pageMountNode"]/div/div[3]/div[2]/div/div/div/div/div[1]/div/div/div/div[2]/div/div[2]/div/div[2]/div/div/div[2]/div/div/span',
            'distance_lbl': '//*[@id="pageMountNode"]/div/div[3]/div[2]/div/div/div/div/div[1]/div/div/div/div[2]/div/div[2]/div/div[3]/div/div/div[2]/span',
            'speed_lbl': '//*[@id="pageMountNode"]/div/div[3]/div[2]/div/div/div/div/div[1]/div/div/div/div[2]/div/div[2]/div/div[4]/div/div/div[2]/div/div/span',
            'elevation_up_lbl': '//*[@id="pageMountNode"]/div/div[3]/div[2]/div/div/div/div/div[1]/div/div/div/div[2]/div/div[2]/div/div[5]/div/div/div[2]/span',
            'elevation_down_lbl': '//*[@id="pageMountNode"]/div/div[3]/div[2]/div/div/div/div/div[1]/div/div/div/div[2]/div/div[2]/div/div[6]/div/div/div[2]/span',
        }
    }

    def __init__(self):
        print('Starting Komoot extraction')

    def extract(self):
        driver = extractors.Selenium.initialize_new_instance()

        driver.get("https://search.dreb.es/?q=ping")
        pong = driver.find_element(By.XPATH, '/html/body/pre')

        print(pong.text)
