import logging
from typing import List

import sqlalchemy
from sqlalchemy.orm import Session

from src.database.Schema import Komoot, Route
from src.model.Komoot.Route import KomootRoute


class MariaDBProvider:

    def __init__(self) -> None:
        self.logger = logging.getLogger(__name__)
        self.engine = sqlalchemy.create_engine("mariadb+mariadbconnector://root:my-secret-pw@127.0.0.1:3306/cip")

        session_maker = sqlalchemy.orm.sessionmaker()
        session_maker.configure(bind=self.engine)
        self.session = session_maker()

    def add_komoot(self, route: KomootRoute) -> None:
        """Add a komoot route to the database.

        Parameters
        ----------
        route : KomootRoute
            The route to add.
        """
        self.logger.debug(f'Inserting route {route.title} to MariaDB')
        komoot = Komoot(title=route.title, link=route.link, difficulty=route.difficulty, distance=route.distance,
                        elevation_up=route.elevation_up, elevation_down=route.elevation_down, duration=route.duration,
                        speed=route.speed, gpx_file=route.gpx_file)
        self.session.add(komoot)
        self.session.commit()

    def add_routes(self, routes: List[Route]) -> None:
        """Add a routes to the database.

        Parameters
        ----------
        routes : List[Route]
            The routes to add.
        """

        for route in routes:
            self.logger.debug(f'Inserting route {route.title} to MariaDB')
            self.session.add(route)

        # commit all routes at once to improve performance
        self.session.commit()
