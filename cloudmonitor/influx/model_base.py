from enum import Enum
from influxdb_client import Point


class Index(Enum):
    TAG = 1
    FIELD = 2


class Column:

    def __init__(self, index):
        self.index = index


class ModelBase:

    def __init__(self, **kwargs):
        for (k, v) in kwargs.items():
            index = self.get_index(self.__class__, k)
            if index:
                setattr(self, k, v)
            else:
                raise NotImplementedError(f'Column {k} not defined in class {self.__class__.__name__}')

    @staticmethod
    def get_index(cls, column):
        for (k, v) in cls.__dict__.items():
            if k == column and isinstance(v, Column):
                return v.index
        return None

    @staticmethod
    def get_mea(cls):
        for (k, v) in cls.__dict__.items():
            if k == '__measurement_name__':
                return v
        return cls.__name__.lower() + 's'

    def convert_to_point(self):
        point = Point(self.get_mea(self.__class__))
        for (k, v) in self.__dict__.items():
            index = self.get_index(self.__class__, k)
            if index:
                if index == Index.TAG:
                    point.tag(k, v)
                else:
                    point.field(k, v)
        return point

    @staticmethod
    def get_tags(cls):
        tags = list()
        for (k, v) in cls.__dict__.items():
            if isinstance(v, Column) and v.index == Index.TAG:
                tags.append(k)
        return tags
