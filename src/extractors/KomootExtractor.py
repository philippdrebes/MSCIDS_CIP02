from selenium.webdriver.chrome.webdriver import WebDriver
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup


class KomootExtractor:
    """
    A class used to extract data from Komoot.com

    Attributes
    ----------
    base_url : str
        a url string used as the base url for all other urls
    discover_url : str
        A combination of the base_url and the discover url
    regions_url : str
        A combination of the base_url and the regions url
    tours_url : str
        A combination of the base_url and the tours url

    Methods
    -------
    extract()
        Extracts all relevant data from the Komoot website.
    """

    base_url = 'https://www.komoot.com'
    discover_url = base_url + '/discover/hiking-trails'
    regions_url = base_url + '/discover/hiking-trails/germany'
    tours_url = base_url + '/discover/hiking-trails/germany/bavaria'

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

    def __init__(self, driver: WebDriver):
        """
        Parameters
        ----------
        driver : WebDriver
            The Selenium WebDriver used to interact with the browser
        """
        self.driver = driver

    def extract(self):
        """Extracts all relevant data from the Komoot website."""

        print('Starting Komoot extraction')
        self.driver.get("https://search.dreb.es/?q=ping")
        pong = self.driver.find_element(By.XPATH, '/html/body/pre')

        print(pong.text)

        self.extract_ch_regions()

    def extract_ch_regions(self):
        """Extracts all regions from the Komoot discover page.

        Raises
        ------
        NotImplementedError
            If no region is passed in
        """

        self.driver.get(self.discover_url)

        # Filter region to Switzerland
        self.driver.find_element(By.XPATH, self.page_objects['discover']['filter_btn']).click()
        self.driver.find_element(By.XPATH, self.page_objects['discover']['filter_country_ch_lbl']).click()

        # Get all regions
        page_source = self.driver.page_source

        soup = BeautifulSoup(page_source, 'lxml')
