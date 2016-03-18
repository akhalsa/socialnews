from Base import Base

from sqlalchemy.dialects.mysql import TIMESTAMP
from sqlalchemy import Column, ForeignKey, Integer, String, func
from sqlalchemy.orm import relationship

class SuggestionVote(Base):
    __tablename__ = 'SuggestionVote'
    # Here we define columns for the table person
    # Notice that each column is also a normal Python instance attribute.
    id = Column(Integer, primary_key=True)
    value = Column(Integer, nullable=False)
    user_id = Column(Integer, ForeignKey('User.ID'))
    suggestion_id = Column(Integer, ForeignKey('Suggestion.id'))
    timestamp = Column(TIMESTAMP, default=func.now())
    
    
    def __repr__(self):
        return "<SuggestionVote(id='%s', suggestion_id='%s', value='%s')>" % (
                                self.id, self.suggestion_id, self.value)

