import os

import datetime

import databases
import sqlalchemy
import pydantic

import ormar

from shortuuid import uuid

database_url = os.environ.get("DATABASE_URL", "sqlite:///test.db")

metadata = sqlalchemy.MetaData()

if database_url.startswith("sqlite"):
    database = databases.Database(database_url)
else:
    database = databases.Database(database_url, min_size=10, max_size=50)


class Document(ormar.Model):
    class Meta:
        tablename = "documents"
        metadata = metadata
        database = database

    id: str = ormar.String(max_length=22, min_length=22, primary_key=True, default=uuid)
    title: str = ormar.String(max_length=1000, nullable=False)
    data: str = ormar.Text(nullable=False)
    data_hash: str = ormar.String(max_length=128, nullable=False)
    creation: datetime.datetime = ormar.DateTime(default=datetime.datetime.utcnow)
    creation_ip: str = ormar.String(max_length=50, nullable=False)
    access: datetime.datetime = ormar.DateTime(default=datetime.datetime.utcnow)
    num_reads: int = ormar.Integer(default=0)
    history: pydantic.Json = ormar.JSON(nullable=False)
