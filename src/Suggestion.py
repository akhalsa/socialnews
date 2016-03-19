from Base import Base

from sqlalchemy.dialects.mysql import TIMESTAMP
from sqlalchemy import Column, ForeignKey, Integer, String, func
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import as_declarative

class Suggestion(Base):
    __tablename__ = 'Suggestion'
    # Here we define columns for the table person
    # Notice that each column is also a normal Python instance attribute.
    id = Column(Integer, primary_key=True)
    text = Column(String(255), nullable=False)
    user_id = Column(Integer, nullable=False)
    timestamp = Column(TIMESTAMP, default=func.now())
    score = Column(Integer)
    
    def __repr__(self):
        return "<Suggestion(id='%s', text='%s', userid='%s')>" % (
                                self.id, self.text, self.user_id)

