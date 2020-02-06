from typing import Union, List, Any
from contextlib import contextmanager
import inspect
from abc import ABC

import peewee as pw
from playhouse import db_url

DATABASE: Union[pw.DatabaseProxy, pw.Database] = pw.DatabaseProxy()


class BaseModel(pw.Model):
    class Meta:
        database = DATABASE

    def __repr__(self):
        return "<{}: {}>".format(
            self.__name__, ", ".join(f"{k}={v}" for k, v in self.__dict.__.items())
        )

    def __str__(self):
        return self.__repr__()


class BaseController(ABC):
    model = None
    database = DATABASE

    @contextmanager
    def transaction(self):
        yield self.database.atomic()

    def create(self, **kwargs) -> BaseModel:
        return self.model.create(**kwargs)

    def get_by_id(self, id: Any, primary_key: str = "id") -> BaseModel:
        field = getattr(self.model, primary_key)
        query = self.model.select().where(field == id)
        return query.get()

    def update(self, row: BaseModel) -> BaseModel:
        row.save()
        return row

    def delete(self, row: BaseModel, recursive=False) -> None:
        row.delete_instance(recursive=recursive)


def _get_models() -> List[BaseModel]:
    """Gets a list of all model classes for tables in the DB"""
    import movienightbot.db.models as models

    return [model for _, model in inspect.getmembers(models, inspect.isclass)]


def initialize_db(url: str) -> pw.Database:
    """Initializes the database

    Parameters
    ----------
    url
        The peewee-formatted URL for connecting to the db

    Returns
    -------
    pw.Database
        The instantiated database object
    """
    db = db_url.connect(url)
    DATABASE.initialize(db)
    tables = _get_models()
    DATABASE.create_tables(tables)
    return DATABASE
