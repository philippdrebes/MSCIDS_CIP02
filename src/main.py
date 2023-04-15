from extractors import SeleniumUtil
from extractors.KomootExtractor import KomootExtractor


def main():
    driver = Selenium.initialize_new_instance()

    komoot = KomootExtractor(driver)
    komoot.extract()


if __name__ == '__main__':
    main()
