class KomootRoute:

    def __init__(self, link: str, title: str, difficulty: str, fitness: str, distance: str, elevation_up: str,
                 elevation_down: str, duration: str, speed: str, gpx_file: str | None = None):
        self.link = link
        self.title = title
        self.difficulty = difficulty
        self.fitness = fitness
        self.distance = distance
        self.elevation_up = elevation_up
        self.elevation_down = elevation_down
        self.duration = duration
        self.speed = speed
        self.gpx_file = gpx_file

    def as_dict(self):
        return {
            'link': self.link,
            'title': self.title,
            'difficulty': self.difficulty,
            'distance': self.distance,
            'elevation_up': self.elevation_up,
            'elevation_down': self.elevation_down,
            'duration': self.duration,
            'speed': self.speed,
            'gpx_file': self.gpx_file
        }
