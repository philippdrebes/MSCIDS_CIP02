import logging
from typing import Dict, List

from bs4 import BeautifulSoup
from selenium.common import ElementNotInteractableException
from selenium.webdriver.chrome.webdriver import WebDriver
from selenium.webdriver.common.by import By

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
    regions_url = base_url + '/guide'
    tours_url = base_url + '/discover/hiking-trails/germany/bavaria'

    page_objects = {
        'discover': {
            'filter_btn': '//*[@id="pageMountNode"]/div/div[3]/div[2]/div/div/main/section[1]/div[2]/div/div[1]/div/div/button[1]',
            'filter_close_btn': '//*[@id="pageMountNode"]/div/div[3]/div[2]/div/div/main/section[1]/div[2]/div/div[2]/div/div[3]/div[2]/button/span',
            'filter_country_ch_lbl': '//*[@id="pageMountNode"]/div/div[3]/div[2]/div/div/main/section[1]/div[2]/div/div[2]/div/div[2]/div/div[13]/label',
            'next_page_btn': '//*[@id="pageMountNode"]/div/div[3]/div[2]/div/div/main/section[1]/div[2]/div/div[3]/div[3]/button',
            'first_region_div': '//*[@id="pageMountNode"]/div/div[3]/div[2]/div/div/main/section[1]/div[2]/div/div[2]/div/div[1]/div/div[3]/a'
        },
        'region': {
            'tour_title_attr': 'data-test-id="tour_title"',
            'tours_list': '#pageMountNode > div > div.tw-bg-beige-light > div.u-bg-desk-column > div > section > div > div > div > div.tw-w-full.lg\:tw-w-3\/5 > div > div > div:nth-child(2) > div > div:nth-child(2) > ul',
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
        self.driver.implicitly_wait(15)
        self.logger = logging.getLogger(__name__)

    def extract(self) -> None:
        """Extracts all relevant data from the Komoot website."""

        self.logger.info('Starting Komoot extraction...')
        regions = self.extract_ch_regions()

        for region in regions:
            self.extract_routes_from_region(region, regions[region])

        self.logger.info('Finished Komoot extraction.')

    def extract_ch_regions(self) -> Dict[str, str]:
        """Extracts all regions from the Komoot discover page. """

        self.logger.info('Extracting all regions in Switzerland...')

        self.driver.get(self.discover_url)
        self.handle_cookie_banner()

        # Filter region to Switzerland
        self.logger.debug('Filter region to Switzerland...')
        self.driver.find_element(By.XPATH, self.page_objects['discover']['filter_btn']).click()
        self.driver.find_element(By.XPATH, self.page_objects['discover']['filter_country_ch_lbl']).click()
        self.driver.find_element(By.XPATH, self.page_objects['discover']['filter_close_btn']).click()

        regions = {}

        # Get all regions
        while True:
            regions = regions | self.extract_region_page()

            # Check if there is a next page button
            try:
                SeleniumUtil.scroll_to_position(self.driver, 1500)
                self.driver.find_element(By.XPATH, self.page_objects['discover']['next_page_btn']).click()
            except ElementNotInteractableException:
                self.logger.info('No more pages to extract.')
                break
            except Exception:
                self.logger.error('Could not extract page.')
                break

        self.logger.info('Extracted {} regions.'.format(len(regions)))
        return regions

    def extract_region_page(self) -> Dict[str, str]:
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

        regions = {}

        self.logger.info('Extracting page: {}'.format(self.driver.current_url))

        # Wait for the regions to appear
        el = self.driver.find_element(By.XPATH, self.page_objects['discover']['first_region_div'])

        page_source = self.driver.page_source
        soup = BeautifulSoup(page_source, 'lxml')

        box = soup.findAll('div', attrs={
            'class': 'js-href-box c-element-preview c-element-preview tw-overflow-hidden c-element-preview--middle'})
        for b in box:
            link = b.find_next('a', attrs={
                'class': 'tw-text-xl sm:tw-text-2xl tw-max-w-full tw-font-bold u-text-shadow tw-text-white tw-mb-0'})
            url = self.base_url + link.attrs['href']
            name = link.text.strip()

            self.logger.info('Extracted region: {} -> {}'.format(name, url))
            regions[name] = url

        return regions

    def extract_routes_from_region(self, region: str, url: str) -> List[str]:
        """Extracts all routes from a region page.

        Parameters
        ----------
        region : str
            The name of the region
        url : str
            The url of the region page

        Raises
        ------
        Exception
            If the current url does not contain the region url
        """

        # if current url does not contain the discover url
        # then we are not on a discover page
        # and should raise an exception
        if self.regions_url not in url:
            err = 'Could not extract routes from a region page, as current url is not a region page.'
            self.logger.error(err)
            raise Exception(err)

        self.logger.info('Extracting routes from region: {} -> {}'.format(region, url))

        routes = []

        self.driver.get(url)

        page_source = self.driver.page_source
        soup = BeautifulSoup(page_source, 'lxml')

        for item in soup.select_one(self.page_objects['region']['tours_list']):
            link = item.find_next('a')
            self.logger.info('Extracted route: {}'.format(link.attrs['href']))
            routes.append(link.attrs['href'])

        self.logger.info('Extracted {} routes from region: {}'.format(len(routes), region))
        return routes

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

        try:
            self.driver.find_element(By.XPATH, btn).click()
            self.logger.info('Cookies {}'.format('accepted' if accept else 'declined'))
        except:
            self.logger.info('No cookie banner could be found')
