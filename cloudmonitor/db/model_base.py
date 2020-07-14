from sqlalchemy.ext import declarative
from sqlalchemy import orm

from oslo_db.sqlalchemy import models


class _ModelBase(models.ModelBase):
    """Base class for CloudMonitor Models."""

    __table_args__ = {'mysql_engine': 'InnoDB'}

    def __iter__(self):
        self._i = iter(orm.object_mapper(self).columns)
        return self

    def next(self):
        n = next(self._i).name
        return n, getattr(self, n)

    __next__ = next

    def __repr__(self):
        """sqlalchemy based automatic __repr__ method."""
        items = ['%s=%r' % (col.name, getattr(self, col.name))
                 for col in self.__table__.columns]
        return "<%s.%s[object at %x] {%s}>" % (self.__class__.__module__,
                                               self.__class__.__name__,
                                               id(self), ', '.join(items))


class ModelBase(_ModelBase):

    @declarative.declared_attr
    def __tablename__(cls):
        # Use the pluralized name of the class as the table name.
        return cls.__name__.lower() + 's'


BASE = declarative.declarative_base(cls=ModelBase)
