import logging
import sys

from extractors import SeleniumUtil
from extractors.KomootExtractor import KomootExtractor
from src.database.MariaDBProvider import MariaDBProvider
from src.loaders.KomootLoader import KomootLoader
from transformers.KomootTransformer import KomootTransformer


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

    # driver = SeleniumUtil.initialize_new_instance()

    stage1_path = 'output/komoot_stage_1.csv'
    stage2_path = 'output/komoot_stage_2.csv'
    gpx_download_path = 'output/gpx'

    # komoot_ext = KomootExtractor(driver, stage1_path, gpx_download_path)
    # komoot_ext.extract()
    # komoot_ext.extract_gpx()
    # SeleniumUtil.close_driver(driver)

    komoot_transformer = KomootTransformer(stage1_path, gpx_download_path, stage2_path)
    komoot_transformer.transform()

    db = MariaDBProvider(stage2_path)
    komoot_loader = KomootLoader(stage2_path, db)
    komoot_loader.load()


if __name__ == '__main__':
    main()
