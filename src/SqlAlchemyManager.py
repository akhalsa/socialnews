import os
import sys
import User
import Base
import datetime
import SuggestionVote
import Suggestion
from sqlalchemy import create_engine
from sqlalchemy.orm import relationship, backref, sessionmaker
    
engine = create_engine('mysql://akhalsa:sophiesChoice1@avtar-news-db-dev.cvnwfvvmmyi7.us-west-2.rds.amazonaws.com/newsdb', echo=True)
Session = sessionmaker(bind=engine)


def insertComment(suggestion_text, uid):
    session = Session()
    suggestion = Suggestion.Suggestion(text=suggestion_text, user_id=uid, score=0)
    session.add(suggestion)
    session.commit()
    
    
def fetchAllComments(uid):
    session = Session()
    q = session.query(User.User, Suggestion.Suggestion).filter(User.User.ID == Suggestion.Suggestion.user_id).all()

    response_json = []
    
    for (User.User, Suggestion) in q:
        single_suggestion = {}
        if(User.User.username is not None):
            single_suggestion["user_name"] = User.User.username
        else:
            single_suggestion["username"] = "user"+str(User.User.ID)
            
        single_suggestion["suggestion_text"] = Suggestion.text
        single_suggestion["timestamp"] = (datetime.datetime.now() - Suggestion.timestamp).total_seconds()
        single_suggestion["score"] = Suggestion.score
        new_q = session.query(SuggestionVote.SuggestionVote).filter(uid == SuggestionVote.SuggestionVote.user_id).all()
        single_suggestion["vote_val"] = 0
        if(len(new_q) > 0):
            single_suggestion["vote_val"] = new_q[0].value

        
        response_json.append(single_suggestion)
        
    print response_json
    return response_json
