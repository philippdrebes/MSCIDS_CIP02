from abc import ABC, abstractmethod


class BaseExtractor(ABC):
    def __init__(self, name):
        self.name = name

    @abstractmethod
    def extract(self):
        print('Starting {} extraction'.format(self.name))
