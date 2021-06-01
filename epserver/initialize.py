import sqlalchemy
from models import metadata, database_url

engine = sqlalchemy.create_engine(database_url)
metadata.create_all(engine)
