import sqlalchemy
from models import metadata

engine = sqlalchemy.create_engine("sqlite:///test.db")
metadata.create_all(engine)
