import logging
import sys

from extractors import SeleniumUtil
from extractors.KomootExtractor import KomootExtractor
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

    stage1_path = './extractors/output/komoot_stage_1.csv'
    stage2_path = './extractors/output/komoot_stage_2.csv'
    gpx_download_path = './extractors/output/gpx'

    # komoot_ext = KomootExtractor(driver, stage1_path, gpx_download_path)
    # komoot_ext.extract()
    # komoot_ext.extract_gpx()
    # SeleniumUtil.close_driver(driver)

    komoot_transformer = KomootTransformer(stage1_path, gpx_download_path, stage2_path)
    komoot_transformer.match_routes_to_gpx()


if __name__ == '__main__':
    main()
