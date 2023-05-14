import sqlalchemy
from sqlalchemy.orm import declarative_base

Base = declarative_base()


class Komoot(Base):  # type: ignore
    __tablename__ = 'komoot'
    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True)
    title = sqlalchemy.Column(sqlalchemy.String(length=512))
    difficulty = sqlalchemy.Column(sqlalchemy.String(length=50))
    distance = sqlalchemy.Column(sqlalchemy.DECIMAL(10, 2))  # type: ignore
    elevation_up = sqlalchemy.Column(sqlalchemy.DECIMAL(10, 2))  # type: ignore
    elevation_down = sqlalchemy.Column(sqlalchemy.DECIMAL(10, 2))  # type: ignore
    duration = sqlalchemy.Column(sqlalchemy.DECIMAL(10, 2))  # type: ignore
    speed = sqlalchemy.Column(sqlalchemy.DECIMAL(10, 2))  # type: ignore
    gpx_file = sqlalchemy.Column(sqlalchemy.String(length=512))
    link = sqlalchemy.Column(sqlalchemy.String(length=512))
