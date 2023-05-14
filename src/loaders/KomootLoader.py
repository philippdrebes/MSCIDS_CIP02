# https://mariadb.com/resources/blog/using-sqlalchemy-with-mariadb-connector-python-part-1/
import logging

import pandas as pd

from src.database.MariaDBProvider import MariaDBProvider
from src.model.Komoot.Route import KomootRoute


class KomootLoader:

    def __init__(self, routes_file: str, db: MariaDBProvider) -> None:
        self.routes_file = routes_file
        self.db = db
        self.logger = logging.getLogger(__name__)

    def load(self):
        self.logger.info('Loading routes into MariaDB')
        routes = [(KomootRoute(
            row.link,
            row.title,
            row.difficulty,
            row.distance_gpx,
            row.elevation_up,
            row.elevation_down,
            row.duration,
            row.speed,
            row.gpx_file
        )) for index, row in pd.read_csv(self.routes_file).iterrows()]

        for route in routes:
            self.logger.debug(f'Adding route {route.title} to MariaDB')
            self.db.addKomoot(route)
