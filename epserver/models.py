import os

import datetime

import databases
import sqlalchemy
import pydantic

import ormar

from shortuuid import uuid

database_url = os.environ.get("DATABASE_URL", "sqlite:///test.db")

metadata = sqlalchemy.MetaData()
database = databases.Database(database_url)


class Document(ormar.Model):
    class Meta:
        tablename = "documents"
        metadata = metadata
        database = database

    id: str = ormar.String(max_length=22, min_length=22, primary_key=True, default=uuid)
    data: str = ormar.Text(nullable=False)
    data_hash: str = ormar.String(max_length=128, nullable=False)
    creation: datetime.datetime = ormar.DateTime(default=datetime.datetime.now)
    access: datetime.datetime = ormar.DateTime(default=datetime.datetime.now)
    num_reads: int = ormar.Integer(default=0)

