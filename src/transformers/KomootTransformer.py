import logging
import os
from typing import Dict, List

from rapidfuzz import process, fuzz, utils
import pandas as pd


class KomootTransformer:
    """Transform the data extracted from komoot.com

    Parameters
    ----------
    routes_file : str
        The path to the csv file containing the routes.
    gpx_folder : str
        The path to the folder containing the gpx files.
    output_path : str
        The path to the output file.

    Attributes
    ----------
    routes_file : str
        The path to the csv file containing the routes.
    gpx_folder : str
        The path to the folder containing the gpx files.
    output_path : str
        The path to the output file.
    logger : logging.Logger
        The logger for this class.
    """

    def __init__(self, routes_file: str, gpx_folder: str, output_path: str) -> None:
        self.routes_file = routes_file
        self.gpx_folder = gpx_folder
        self.output_path = output_path
        self.logger = logging.getLogger(__name__)

    def match_routes_to_gpx(self) -> None:
        """Match routes to gpx files based on their title."""

        # rename gpx files and add them to the output file
        routes = pd.read_csv(self.routes_file)
        gpx_files = [x for x in os.listdir(self.gpx_folder) if x.endswith('.gpx')]

        self.logger.info(f'Found {len(gpx_files)} gpx files')
        self.logger.info(f'Found {len(routes)} routes')
        self.logger.info(f'Matching gpx files to routes')

        routes['gpx_file'] = routes.apply(lambda row: self.find_gpx_file(row, gpx_files), axis=1)

        self.logger.info(f'Writing output to {self.output_path}')
        routes.to_csv(self.output_path, index=False)

    @staticmethod
    def find_gpx_file(row, files: List[str]) -> str | None:
        """Find the gpx file that matches the route title best.
        Pops the file from the list, so it can't be matched again.

        Parameters
        ----------
        row : pandas.Series
            The row of the route dataframe.
        files : List[str]
            The list of gpx files.

        Returns
        -------
        str
            The name of the gpx file that matches the route title best.
        """

        if files is None or len(files) == 0:
            return None

        # replace common english words with german words
        title = row.title.replace('loop', 'Runde').replace('from', 'von').replace('to', 'nach')

        # find gpx file where the file name best matches the route title
        (best_match, score, idx) = process.extractOne(title, files, scorer=fuzz.WRatio, processor=utils.default_process)

        # pop the file from the list, so it can't be matched again
        files.pop(idx)

        return best_match
