import sqlalchemy
from models import Category, Item, metadata, database

engine = sqlalchemy.create_engine("sqlite:///test.db")
metadata.create_all(engine)
