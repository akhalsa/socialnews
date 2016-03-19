import os
import sys
import Suggestion as su
import User
import Base
import datetime
import SuggestionVote
from sqlalchemy import create_engine
from sqlalchemy.orm import relationship, backref, sessionmaker
    
engine = create_engine('mysql://akhalsa:sophiesChoice1@avtar-news-db-dev.cvnwfvvmmyi7.us-west-2.rds.amazonaws.com/newsdb', echo=True)
Session = sessionmaker(bind=engine)
if(engine):
    print "engine passed"
else:
    print "no engine"

def insertComment(suggestion_text, uid):
    session = Session()
    suggestion = su.Suggestion(text=suggestion_text, user_id=uid, score=0)
    session.add(suggestion)
    session.commit()
    
    
def fetchAllComments(uid):
    session = Session()
    q = session.query(User.User, su.Suggestion).filter(User.User.ID == su.Suggestion.user_id).all()

    response_json = []
    
    for (User.User, su.Suggestion) in q:
        single_suggestion = {}
        if(User.User.username is not None):
            single_suggestion["user_name"] = User.User.username
        else:
            single_suggestion["username"] = "user"+str(User.User.ID)
            
        single_suggestion["suggestion_text"] = su.Suggestion.text
        single_suggestion["timestamp"] = (datetime.datetime.now() - su.Suggestion.timestamp).total_seconds()
        single_suggestion["score"] = su.Suggestion.score
        new_q = session.query(SuggestionVote.SuggestionVote).filter(uid == SuggestionVote.SuggestionVote.user_id).all()
        single_suggestion["vote_val"] = 0
        if(len(new_q) > 0):
            single_suggestion["vote_val"] = new_q[0].value

        
        response_json.append(single_suggestion)
        
    print response_json
    return response_json
