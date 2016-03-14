import os
import sys
from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy import create_engine

from sqlalchemy.dialects.mysql import TIMESTAMP
 
Base = declarative_base()
 
class Suggestion(Base):
    __tablename__ = 'Suggestion'
    # Here we define columns for the table person
    # Notice that each column is also a normal Python instance attribute.
    id = Column(Integer, primary_key=True)
    text = Column(String(255), nullable=False)
    user_id = Column(Integer, nullable=False)
    timestamp = Column(TIMESTAMP, nullable=False)
    
    
    def __repr__(self):
        return "<Suggestion(id='%s', text='%s', userid='%s')>" % (
                                self.id, self.text, self.user_id)
    
 
 

engine = create_engine('mysql://akhalsa:sophiesChoice1@avtar-news-db-dev.cvnwfvvmmyi7.us-west-2.rds.amazonaws.com/newsdb', echo=True)

Base.metadata.create_all(engine)

