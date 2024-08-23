import os
import sqlalchemy

from databases import Database
from dotenv import load_dotenv


load_dotenv()

db = Database(os.getenv("DATABASE_URL"))

metadata = sqlalchemy.MetaData()
