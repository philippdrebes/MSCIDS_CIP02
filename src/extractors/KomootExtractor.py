import logging

from selenium.common import NoSuchElementException, ElementNotInteractableException
from selenium.webdriver.chrome.webdriver import WebDriver
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup

from src.extractors import SeleniumUtil


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
            'next_page_btn': '/html/body/div[1]/div/div[3]/div[2]/div/div/main/section[1]/div[2]/div/div[4]/div[3]/button',
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
        },
        'cookie_banner': {
            'accept_btn': '//*[@id="gdpr_banner_portal"]/div/div/div/div[2]/div/div[1]/button',
            'decline_btn': '//*[@id="gdpr_banner_portal"]/div/div/div/div[2]/div/div[3]/button'
        }
    }

    def __init__(self, driver: WebDriver) -> None:
        """
        Parameters
        ----------
        driver : WebDriver
            The Selenium WebDriver used to interact with the browser
        """
        self.driver = driver
        self.logger = logging.getLogger(__name__)

    def extract(self) -> None:
        """Extracts all relevant data from the Komoot website."""

        self.logger.info('Starting Komoot extraction...')
        self.extract_ch_regions()

    def extract_ch_regions(self) -> None:
        """Extracts all regions from the Komoot discover page.

        Raises
        ------
        NotImplementedError
            If no region is passed in
        """

        self.logger.info('Extracting all regions in Switzerland...')

        self.driver.get(self.discover_url)
        self.handle_cookie_banner()

        # Filter region to Switzerland
        self.logger.debug('Filter region to Switzerland...')
        # SeleniumUtil.scroll_to_position(self.driver, 250)
        self.driver.find_element(By.XPATH, self.page_objects['discover']['filter_btn']).click()
        self.driver.find_element(By.XPATH, self.page_objects['discover']['filter_country_ch_lbl']).click()

        # Get all regions
        while True:
            self.extract_region_page()

            # Check if there is a next page button
            try:
                SeleniumUtil.scroll_to_position(self.driver, 900)
                self.driver.find_element(By.XPATH, self.page_objects['discover']['next_page_btn']).click()
            except ElementNotInteractableException:
                self.logger.info('No more pages to extract.')
                break
            except Exception:
                self.logger.error('Could not extract page.')
                break

    def extract_region_page(self) -> None:
        """Extracts all regions from a discover page.

        Raises
        ------
        Exception
            If the current url does not contain the discover url
        """

        # if current url does not contain the discover url
        # then we are not on a discover page
        # and should raise an exception
        if self.discover_url not in self.driver.current_url:
            err = 'Could not extract regions from a discover page, as current url is not a discover page.'
            self.logger.error(err)
            raise Exception(err)

        page_source = self.driver.page_source
        soup = BeautifulSoup(page_source, 'lxml')

    def handle_cookie_banner(self, accept: bool = False) -> None:
        """Handles the cookie banner if it appears.

        Parameters
        ----------
        accept : bool
            If true, the accept button will be clicked. If false, the decline button will be clicked.
            default: False
        """

        btn = self.page_objects['cookie_banner']['decline_btn']
        if accept:
            btn = self.page_objects['cookie_banner']['accept_btn']

        self.logger.info('Searching for and handling cookie banner...')

        self.driver.implicitly_wait(20)  # Wait for the cookie banner to appear

        try:
            self.driver.find_element(By.XPATH, btn).click()
            self.logger.info('Cookies {}'.format('accepted' if accept else 'declined'))
        except:
            self.logger.info('No cookie banner could be found')
