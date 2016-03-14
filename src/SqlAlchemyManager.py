import sqlalchemy

from sqlalchemy import create_engine

engine = create_engine('sqlite:///:memory:', echo=True)

engine = create_engine('mysql://akhalsa:sophiesChoice1@avtar-news-db-dev.cvnwfvvmmyi7.us-west-2.rds.amazonaws.com', echo=True)
