from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.dialects.mysql import TIMESTAMP
from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

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
    