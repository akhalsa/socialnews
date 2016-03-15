import os
import sys
import Suggestion
import Base
from sqlalchemy import create_engine
    
engine = create_engine('mysql://akhalsa:sophiesChoice1@avtar-news-db-dev.cvnwfvvmmyi7.us-west-2.rds.amazonaws.com/newsdb', echo=True)

Base.Base.metadata.create_all(engine)

