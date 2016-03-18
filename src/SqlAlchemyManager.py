import os
import sys
import Suggestion
import Base
from sqlalchemy import create_engine
from sqlalchemy.orm import relationship, backref, sessionmaker
    
engine = create_engine('mysql://akhalsa:sophiesChoice1@avtar-news-db-dev.cvnwfvvmmyi7.us-west-2.rds.amazonaws.com/newsdb', echo=True)
Session = sessionmaker(bind=engine)

def insertComment(suggestion_text, uid):
    session = Session()
    suggestion = Suggestion.Suggestion(text=suggestion_text, user_id=uid)
    session.add(suggestion)
    session.commit()
    
    
def fetchAllComments():
    session = Session()
    for instance in session.query(Suggestion).order_by(Suggestion.id):
        print instance.text
