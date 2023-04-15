import logging
import platform
from typing import Union

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.webdriver import WebDriver

logger = logging.getLogger(__name__)


def initialize_new_instance() -> WebDriver:
    logger.info('Initializing new instance of Chrome')
    plt = platform.system()
    if plt == 'Darwin':
        logger.info('Running on macOS')
        option = webdriver.ChromeOptions()
        option.binary_location = r'/Applications/Brave Browser.app/Contents/MacOS/Brave Browser'
        driver_service = Service('/opt/homebrew/bin/chromedriver')

        driver = webdriver.Chrome(service=driver_service, options=option)
        logger.info('Initialized new instance of Chrome')
        return driver

    logger.info('Running on Linux or Windows')
    driver = webdriver.Chrome()
    logger.info('Initialized new instance of Chrome')
    return driver


def scroll_to_bottom(driver: WebDriver) -> None:
    scroll_to_position(driver, 'document.body.scrollHeight')
    logger.debug('Scrolled to bottom of page')


def scroll_to_position(driver: WebDriver, position: Union[int, str]) -> None:
    driver.execute_script(f"window.scrollTo(0, {position});")
    logger.debug('Scrolled to position %s', position)
