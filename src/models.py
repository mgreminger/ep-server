from typing import Optional

import databases
import sqlalchemy

import ormar

metadata = sqlalchemy.MetaData()
database = databases.Database("sqlite:///test.db")

class Category(ormar.Model):
    class Meta:
        tablename = "categories"
        metadata = metadata
        database = database

    id: int = ormar.Integer(primary_key=True)
    name: str = ormar.String(max_length=100)


class Item(ormar.Model):
    class Meta:
        tablename = "items"
        metadata = metadata
        database = database

    id: int = ormar.Integer(primary_key=True)
    name: str = ormar.String(max_length=100)
    category: Optional[Category] = ormar.ForeignKey(Category, nullable=True)
