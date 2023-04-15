import logging
import sys

from extractors import SeleniumUtil
from extractors.KomootExtractor import KomootExtractor


def setup_logging() -> None:
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S',
        handlers=[
            logging.StreamHandler(sys.stdout)
        ]
    )


def main() -> None:
    setup_logging()
    logger = logging.getLogger(__name__)
    logger.info('Starting main.py')

    driver = SeleniumUtil.initialize_new_instance()

    komoot = KomootExtractor(driver)
    komoot.extract()


if __name__ == '__main__':
    main()
