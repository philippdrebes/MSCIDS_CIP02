import logging

import sqlalchemy
from sqlalchemy.orm import Session

from src.database.Schema import Komoot
from src.model.Komoot.Route import KomootRoute


class MariaDBProvider:

    def __init__(self, routes_file: str) -> None:
        self.logger = logging.getLogger(__name__)
        self.engine = sqlalchemy.create_engine("mariadb+mariadbconnector://root:my-secret-pw@127.0.0.1:3306/cip")

        session_maker = sqlalchemy.orm.sessionmaker()
        session_maker.configure(bind=self.engine)
        self.session = session_maker()

    def addKomoot(self, route: KomootRoute) -> None:
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
