import logging
import os
import re
from itertools import islice
from time import sleep

import pandas as pd
from typing import Dict, List

from bs4 import BeautifulSoup
from selenium.common import ElementNotInteractableException, NoSuchElementException
from selenium.webdriver.chrome.webdriver import WebDriver
from selenium.webdriver.common.by import By

from src.extractors import SeleniumUtil
from src.model.Komoot.Route import KomootRoute
import keyring


class KomootExtractor:
    """
    A class used to extract data from Komoot.com

    Attributes
    ----------
    base_url : str
        a url string used as the base url for all other urls
    discover_url : str
        A combination of the base_url and the discover url
    region_url : str
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
    region_url = base_url + '/guide'
    route_url = base_url + '/smarttour'
    login_url = 'https://account.komoot.com/signin'
    max_retries = 3
    retry_wait_seconds = 5

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
            'gpx_download_btn': '//*[@id="pageMountNode"]/div/div[3]/div[2]/div/div/div/div/div[2]/div/div/div/div[1]/div/div[2]/div/ul/li[3]/button'
        },
        'login': {
            'email_input': '//*[@id="email"]',
            'password_input': '//*[@id="password"]',
            'continue_btn': '//*[@id="pageMountNode"]/div/div[1]/div[2]/div/div[1]/form/div[4]/button',
            'login_btn': '//*[@id="pageMountNode"]/div/div[1]/div[2]/form/div/div[5]/button'
        },
        'cookie_banner': {
            'accept_btn': '//*[@id="gdpr_banner_portal"]/div/div/div/div[2]/div/div[1]/button',
            'decline_btn': '//*[@id="gdpr_banner_portal"]/div/div/div/div[2]/div/div[3]/button'
        }
    }

    def __init__(self, driver: WebDriver, output_path: str, gpx_download_path: str) -> None:
        """
        Parameters
        ----------
        driver : WebDriver
            The Selenium WebDriver used to interact with the browser
        """
        self.driver = driver
        self.driver.implicitly_wait(15)
        self.output_path = output_path
        self.gpx_download_path = gpx_download_path
        self.logger = logging.getLogger(__name__)

    def extract(self) -> None:
        """Extracts all relevant data from the Komoot website."""

        self.logger.info('Starting Komoot extraction...')
        regions = self.extract_ch_regions()

        existing = self.read_existing_data()

        routes: List[KomootRoute] = existing

        # split regions dictionary into chunks of 20
        for chunk in self.chunks(regions, 20):
            for region in chunk:
                for route in self.extract_routes_from_region(region, chunk[region]):

                    # check if route is already in existing routes by comparing the link
                    if route not in [r.link for r in routes]:
                        routes.append(self.extract_route(route))
                        sleep(5)  # Sleep 5 seconds to avoid getting rate limited

            self.logger.info('Saving current state...')
            self.save(routes)  # Save routes after each chunk to avoid losing data
            sleep(120)  # Sleep for 120 seconds to avoid getting rate limited

        self.logger.info('Finished Komoot extraction.')

        self.logger.info('Saving Komoot data...')
        self.save(routes)
        self.logger.info('Saved Komoot data.')

    def extract_gpx(self) -> None:
        """ Extracts the GPX files for all routes in the output file.  """

        existing = self.read_existing_data()

        self.handle_komoot_login()

        existing_gpx_files = os.listdir(self.gpx_download_path)

        for idx, route in enumerate(existing):
            pattern = re.compile(route.title + "\.gpx$")
            for filepath in existing_gpx_files:
                if pattern.match(filepath):
                    self.logger.info(f'GPX for route {route.title} already exists. Skipping...')
                    continue

            self.logger.info(f'Downloading GPX for route {route.title}...')

            link = route.link.replace('https://www.komoot.com/', 'https://www.komoot.de/')

            self.driver.get(link)
            self.driver.find_element(By.XPATH, self.page_objects['tour']['gpx_download_btn']).click()
            self.logger.info(f'Downloaded GPX for route {route.title}.')
            sleep(5)  # Sleep 5 seconds to avoid getting rate limited
            if idx % 40 == 0:
                self.logger.info('Sleeping for 120 seconds...')
                sleep(120)

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
        # then we are not on a discover page and should raise an exception
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

        # if current url does not contain the region url
        # then we are not on a region page and should raise an exception
        if self.region_url not in url:
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

    def extract_route(self, url: str, retry_count: int = 0) -> KomootRoute:
        """Extracts all relevant data from a tour page.

        Parameters
        ----------
        url : str
            The url of the tour page
        retry_count : int (optional)
            The number of retries
            default: 0

        Raises
        ------
        Exception
            If the current url does not contain the route url
        """

        # if current url does not contain the route url
        # then we are not on a route page and should raise an exception
        if self.route_url not in url:
            err = 'Could not extract routes from a region page, as current url is not a region page.'
            self.logger.error(err)
            raise Exception(err)

        self.logger.info('Extracting data from tour: {}'.format(url))

        try:
            self.driver.get(url)

            title = self.driver.find_element(By.XPATH, self.page_objects['tour']['title_lbl']).text.strip()
            difficulty = self.driver.find_element(By.XPATH, self.page_objects['tour']['difficulty_lbl']).text.strip()
            distance = self.driver.find_element(By.XPATH, self.page_objects['tour']['distance_lbl']).text.strip()
            elevation_up = self.driver.find_element(By.XPATH,
                                                    self.page_objects['tour']['elevation_up_lbl']).text.strip()
            elevation_down = self.driver.find_element(By.XPATH,
                                                      self.page_objects['tour']['elevation_down_lbl']).text.strip()
            duration = self.driver.find_element(By.XPATH, self.page_objects['tour']['duration_lbl']).text.strip()
            speed = self.driver.find_element(By.XPATH, self.page_objects['tour']['speed_lbl']).text.strip()

            self.logger.info('Extracted data from tour: {} -> {}'.format(title, url))

            return KomootRoute(url, title, difficulty, distance, elevation_up, elevation_down, duration, speed)
        except Exception as e:
            self.logger.error('Could not extract data from tour: {}'.format(url))
            self.logger.error(e)
            if retry_count < self.max_retries:
                wait_seconds = self.retry_wait_seconds ** (retry_count + 1)

                self.logger.info('Retrying in {} seconds...'.format(wait_seconds))
                sleep(wait_seconds)
                return self.extract_route(url, retry_count + 1)
            else:
                self.logger.info('Max retries exceeded. Skipping...')
                return None

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

    def handle_komoot_login(self) -> None:
        """Handles the Komoot login process."""

        keyringServiceName = "Komoot Login"
        # keyring.set_password(keyringServiceName, "philipp.drebes@gmail.com", "^Wot2Y$3a@^krKN6V3")

        credentials = keyring.get_credential(keyringServiceName, "philipp.drebes@gmail.com")

        self.logger.info('Logging in to Komoot...')
        self.driver.get(self.login_url)
        self.driver.find_element(By.XPATH, self.page_objects['login']['email_input']).send_keys(credentials.username)
        self.driver.find_element(By.XPATH, self.page_objects['login']['continue_btn']).click()
        self.driver.find_element(By.XPATH, self.page_objects['login']['password_input']).send_keys(credentials.password)
        self.driver.find_element(By.XPATH, self.page_objects['login']['login_btn']).click()
        sleep(20)
        self.logger.info('Logged in to Komoot.')

    def save(self, routes: List[KomootRoute]) -> None:
        """Saves the given routes to a csv file.

        Parameters
        ----------
        routes : List[KomootRoute]
            The routes to save
        """

        self.logger.info('Saving {} routes to csv file...'.format(len(routes)))

        df = pd.DataFrame([x.as_dict() for x in routes])
        df.to_csv(self.output_path, index=False)

        self.logger.info('Saved {} routes to csv file.'.format(len(routes)))

    def read_existing_data(self) -> List[KomootRoute]:
        return [(KomootRoute(
            row.link,
            row.title,
            row.difficulty,
            row.distance,
            row.elevation_up,
            row.elevation_down,
            row.duration,
            row.speed,
        )) for index, row in pd.read_csv(self.output_path).iterrows()]

    @staticmethod
    def chunks(data: Dict, size: int = 10):
        """Yield successive n-sized chunks from data.

        Parameters
        ----------
        data : Dict
            The data to split
        size : int
            The size of each chunk
            default: 10
        """

        it = iter(data)
        for i in range(0, len(data), size):
            yield {k: data[k] for k in islice(it, size)}
