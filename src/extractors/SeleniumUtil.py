import logging
import platform
from typing import Union

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.webdriver import WebDriver

logger = logging.getLogger(__name__)


def initialize_new_instance() -> WebDriver:
    """Initializes a new instance of the Chrome WebDriver.
    If the platform is macOS, the Brave browser is used instead of Chrome.
    Also, it is assumed that the chromedriver was installed via Homebrew.

    Returns
    -------
    WebDriver
        The initialized WebDriver
    """
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
    """Scrolls to the bottom of the page.

    Parameters
    ----------
    driver : WebDriver
        The Selenium WebDriver used to interact with the browser
    """
    scroll_to_position(driver, 'document.body.scrollHeight')
    logger.debug('Scrolled to bottom of page')


def scroll_to_position(driver: WebDriver, position: Union[int, str]) -> None:
    """Scrolls to the given position.

    Parameters
    ----------
    driver : WebDriver
        The Selenium WebDriver used to interact with the browser
    position : int or str
        The position to scroll to.
        If int, the position in pixels.
        If str, for example 'document.body.scrollHeight'.
    """
    driver.execute_script(f"window.scrollTo(0, {position});")
    logger.debug('Scrolled to position %s', position)
