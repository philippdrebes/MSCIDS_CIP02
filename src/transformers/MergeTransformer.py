import logging

import pandas as pd


class MergeTransformer:
    """Merge the data from the different sources.

    Parameters
    ----------
    komoot : str
        The path to the csv file containing the routes from komoot.
    sac : str
        The path to the csv file containing the routes from sac-cas.ch.
    schweizmobil : str
        The path to the csv file containing the routes from schweizmobil.ch.

    Attributes
    ----------
    komoot : pd.DataFrame
        The dataframe containing the routes from komoot.
    sac : pd.DataFrame
        The dataframe containing the routes from sac-cas.ch.
    schweizmobil : pd.DataFrame
        The dataframe containing the routes from schweizmobil.ch.
    logger : logging.Logger
        The logger for this class.
    """

    columns = [
        'source',
        'title',
        'distance',
        'elevation_up',
        'elevation_down',
        'duration',
        'difficulty',
        'link',
    ]

    def __init__(self, komoot: str, sac: str, schweizmobil: str):
        self.logger = logging.getLogger(__name__)
        self.komoot = pd.read_csv(komoot)
        self.sac = pd.read_csv(sac)
        self.schweizmobil = pd.read_csv(schweizmobil)

    def merge_sources(self):
        """Merge the data from the different sources.

        Returns
        -------
        None
        """

        # Prepare the data from the different sources, so that they can be merged
        self.prepare_komoot()
        self.prepare_sac()
        self.prepare_schweizmobil()

        # Merge the data from the different sources
        merged_df = pd.concat([self.komoot, self.sac, self.schweizmobil], ignore_index=True)

        # Write the output to a csv file
        merged_df.to_csv('output/merged.csv', index=False)

    def prepare_komoot(self) -> None:
        """Prepare the data from komoot.

        Returns
        -------
        None
        """

        # Add the source column to the dataframe
        self.komoot['source'] = 'komoot'

        # Map the difficulty levels to the same values as the other sources
        difficulty_mapping = {
            'Easy': 'easy',
            'Intermediate': 'medium',
            'Expert': 'difficult',
        }
        self.komoot['difficulty'] = self.komoot.apply(lambda row: difficulty_mapping[row.difficulty], axis=1)

        # Convert the duration to a time object
        self.komoot['duration'] = pd.to_datetime(self.komoot['duration'], unit='m').dt.time

        # Convert the distance, elevation_up and elevation_down to floats
        self.komoot['distance'] = self.komoot['distance'].astype('float')
        self.komoot['elevation_up'] = self.komoot['elevation_up'].astype('float')
        self.komoot['elevation_down'] = self.komoot['elevation_down'].astype('float')

        # Select the columns that are needed
        self.komoot = self.komoot[self.columns]

    def prepare_sac(self) -> None:
        """Prepare the data from sac-cas.ch.

        Returns
        -------
        None
        """

        # Add the source column to the dataframe
        self.sac['source'] = 'sac'

        # Drop the columns that are not needed and rename the columns to match the other sources
        self.sac.drop(columns=['difficulty'], inplace=True)
        self.sac = self.sac.rename(columns={'distance_clean': 'distance', 'ascent_clean': 'elevation_up',
                                            'descent_clean': 'elevation_down', 'difficulty_calc1': 'difficulty'})

        # Calculate the duration
        self.sac['duration'] = self.sac['time_ascent_clean'] + self.sac['time_descent_clean']

        # Replace the 'na' values with 0 and convert the columns to the correct type
        self.sac['elevation_up'].replace('na', '0', inplace=True)
        self.sac['elevation_down'].replace('na', '0', inplace=True)
        self.sac['distance'] = self.sac['distance'].astype('float')
        self.sac['elevation_up'] = self.sac['elevation_up'].astype('float')
        self.sac['elevation_down'] = self.sac['elevation_down'].astype('float')

        # No need to map the difficulty levels, they are already the same as the other sources

        # Select the columns that are needed
        self.sac = self.sac[self.columns]

    def prepare_schweizmobil(self) -> None:
        """Prepare the data from schweizmobil.ch.

        Returns
        -------
        None
        """

        # Add the source column to the dataframe
        self.schweizmobil['source'] = 'schweizmobil'

        # Rename the columns to match the other sources
        self.schweizmobil = self.schweizmobil.rename(
            columns={'url': 'link', 'name': 'title', 'altitude_up': 'elevation_up',
                     'altitude_down': 'elevation_down', 'difficulty_level': 'difficulty'})

        # Calculate the duration
        self.schweizmobil['duration'] = pd.to_datetime(self.schweizmobil['duration'], unit='m').dt.time

        # Map the difficulty levels to the same values as the other sources
        difficulty_mapping = {
            'leicht': 'easy',
            'mittel': 'medium',
            'difficult': 'difficult',
        }
        self.schweizmobil['difficulty'] = self.schweizmobil.apply(lambda row: difficulty_mapping[row.difficulty],
                                                                  axis=1)

        # Convert the columns to the correct type
        self.schweizmobil['distance'] = self.schweizmobil['distance'].astype('float')
        self.schweizmobil['elevation_up'] = self.schweizmobil['elevation_up'].astype('float')
        self.schweizmobil['elevation_down'] = self.schweizmobil['elevation_down'].astype('float')

        # Select the columns that are needed
        self.schweizmobil = self.schweizmobil[self.columns]
