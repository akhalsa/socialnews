import os
import sys

from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import create_engine
import Suggestion.py

engine = create_engine('mysql://akhalsa:sophiesChoice1@avtar-news-db-dev.cvnwfvvmmyi7.us-west-2.rds.amazonaws.com/newsdb', echo=True)

Base.metadata.create_all(engine)

