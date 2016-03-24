from Base import Base

from sqlalchemy.dialects.mysql import TIMESTAMP
from sqlalchemy import Column, ForeignKey, Integer, String, func
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import as_declarative

class FBPost(Base):
    __tablename__ = 'FBPost'
    # Here we define columns for the table person
    # Notice that each column is also a normal Python instance attribute.
    id = Column(Integer, primary_key=True)
    tweet_id = Column(String(255), nullable=False)
    
    def __repr__(self):
        return "<FBPost(id='%s', tweet_id='%s')>" % (self.id, self.text)
