import argparse

import sqlalchemy
from models import metadata, database_url

parser = argparse.ArgumentParser()
parser.add_argument("--drop_all", help="Clear defined tables in database", action="store_true")
args = parser.parse_args()

engine = sqlalchemy.create_engine(database_url)

if args.drop_all:
  print(f"Delete all values from tables in {database_url}? Be carefull, this cannot be reversed!")
  confirm = input('[yes/no]? ')
  if confirm.lower() == "yes":
    print("Deleting table content")
    metadata.drop_all(engine)
  else:
    print("Canceling operation")
    exit()

metadata.create_all(engine)
