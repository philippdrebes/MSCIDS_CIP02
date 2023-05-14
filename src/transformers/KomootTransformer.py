import logging
import os
import re
from typing import Dict, List

import gpxpy
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

    routes: pd.DataFrame
    emoji_pattern = re.compile(r"[\U00010000-\U0010FFFF]")

    def __init__(self, routes_file: str, gpx_folder: str, output_path: str) -> None:
        self.routes_file = routes_file
        self.gpx_folder = gpx_folder
        self.output_path = output_path
        self.logger = logging.getLogger(__name__)

    def transform(self) -> None:
        """Transform the data.

        Returns
        -------
        None
        """

        self.routes = pd.read_csv(self.routes_file)

        self.clean_titles()
        self.convert_units()
        self.match_routes_to_gpx()
        self.load_data_from_gpx()

        self.logger.info(f'Writing output to {self.output_path}')
        self.routes.to_csv(self.output_path, index=False)

    def clean_titles(self) -> None:
        self.routes['title'] = self.routes.apply(lambda row: self.strip_emojis(row.title), axis=1)

    def load_data_from_gpx(self):
        self.logger.info('Loading data from gpx files')
        self.routes['distance_gpx'] = self.routes.apply(
            lambda row: self.read_distance_from_gpx(os.path.join(self.gpx_folder, row.gpx_file)), axis=1)

    def convert_units(self):
        """Convert the units of the routes.

        Returns
        -------
        None
        """
        self.logger.info('Converting units')
        self.routes['distance'] = self.routes.apply(lambda row: self.convert_distance(row.distance), axis=1)
        self.routes['elevation_up'] = self.routes.apply(lambda row: self.convert_elevation(row.elevation_up), axis=1)
        self.routes['elevation_down'] = self.routes.apply(lambda row: self.convert_elevation(row.elevation_down),
                                                          axis=1)
        self.routes['duration'] = self.routes.apply(lambda row: self.convert_duration(row.duration), axis=1)
        self.routes['speed'] = self.routes.apply(lambda row: self.convert_speed(row.speed), axis=1)

    def convert_duration(self, duration: str) -> int | None:
        """Converts the duration to minutes.

        Parameters
        ----------
        duration : str
            The duration in hours e.g. 02:35

        Returns
        -------
        int
            The duration in minutes..
        """

        if duration is None or duration == '':
            return None

        hours, minutes = duration.split(':')
        return int(hours) * 60 + int(minutes)

    def convert_speed(self, speed: str) -> float | None:
        """Convert the speed from mph to kmh.

        Parameters
        ----------
        speed : str
            The speed in mph.

        Returns
        -------
        str
            The speed in kmh.
        """

        if speed is None or speed == '':
            return None

        miles = float(speed.replace('mph', '').strip())
        return round(self.convert_mi_to_km(miles), 2)

    def convert_distance(self, distance: str) -> float | None:
        """Convert the distance from miles to kilometers.

        Parameters
        ----------
        distance : str
            The distance in miles.

        Returns
        -------
        str
            The distance in kilometers.
        """

        if distance is None or distance == '':
            return None

        miles = float(distance.replace('mi', '').replace(',', '').strip())
        return round(self.convert_mi_to_km(miles), 2)

    def convert_elevation(self, elevation: str) -> float | None:
        """Convert the distance from feet to meters.

        Parameters
        ----------
        elevation : str
            The elevation in feet.

        Returns
        -------
        str
            The elevation in meters.
        """

        if elevation is None or elevation == '':
            return None

        feet = float(elevation.replace('ft', '').replace(',', '').strip())
        return round(self.convert_ft_to_m(feet), 2)

    def match_routes_to_gpx(self) -> None:
        """Match routes to gpx files based on their title."""

        gpx_files = [x for x in os.listdir(self.gpx_folder) if x.endswith('.gpx')]

        self.logger.info(f'Found {len(gpx_files)} gpx files')
        self.logger.info(f'Found {len(self.routes)} routes')

        self.logger.info(f'Cleaning gpx file names')
        for gpx_file in gpx_files:
            old_filepath = os.path.join(self.gpx_folder, gpx_file)
            new_filepath = os.path.join(self.gpx_folder, self.strip_emojis(gpx_file))
            os.rename(old_filepath, new_filepath)

        # reload the gpx files after renaming
        gpx_files = [x for x in os.listdir(self.gpx_folder) if x.endswith('.gpx')]

        self.logger.info(f'Matching gpx files to routes')
        self.routes['gpx_file'] = self.routes.apply(lambda row: self.find_gpx_file(row, gpx_files), axis=1)

    def strip_emojis(self, text: str) -> str:
        """Strips all emojis from text.

        Parameters
        ----------
        text : str
            The text to strip the emojis from.

        Returns
        -------
        str
            The text without emojis.
        """
        return self.emoji_pattern.sub(r'', text)

    @staticmethod
    def read_distance_from_gpx(gpx_path: str) -> float | None:
        """Read the distance from the gpx file.

        Parameters
        ----------
        gpx_path : str
            The path to the gpx file.

        Returns
        -------
        float
            The distance in km.
        """
        gpx = gpxpy.parse(open(gpx_path, 'r'))
        length_m = gpx.length_2d()
        length_km = round(length_m / 1000, 2)
        return length_km

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

    @staticmethod
    def convert_mi_to_km(mi: float) -> float:
        """Convert miles to kilometers

        Parameters
        ----------
        mi : float
            The distance in miles.
        """
        return mi * 1.609344

    @staticmethod
    def convert_ft_to_m(ft: float) -> float:
        """Convert feet to meters

        Parameters
        ----------
        ft : float
            The distance in feet.
        """
        return ft * 0.3048
