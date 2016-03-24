import os
import sys
import User
import Base
import datetime
import SuggestionVote
import Suggestion
import FBPost
import loadenvironment
from sqlalchemy import create_engine
from sqlalchemy.orm import relationship, backref, sessionmaker
    
engine = create_engine(loadenvironment.getSqlEngineString(), echo=True)
Session = sessionmaker(bind=engine)


def insertSuggestion(suggestion_text, uid):
    session = Session()
    suggestion = Suggestion.Suggestion(text=suggestion_text, user_id=uid, score=0)
    session.add(suggestion)
    session.commit()
    session.close()
    
    
def fetchAllSuggestions(uid):
    session = Session()
    print type(Suggestion.Suggestion).__name__
    
    
    q = session.query(User.User, Suggestion.Suggestion).filter(User.User.ID == Suggestion.Suggestion.user_id)

    response_json = []
    
    for row in q:

        single_suggestion = {}
        if(row[0].username is not None):
            single_suggestion["user_name"] = row[0].username
        else:
            single_suggestion["username"] = "user"+str(row[0].ID)
        single_suggestion["id"] = row[1].id
        single_suggestion["suggestion_text"] = row[1].text
        single_suggestion["timestamp"] = (datetime.datetime.now() - row[1].timestamp).total_seconds()
        single_suggestion["score"] = row[1].score
        new_q = session.query(SuggestionVote.SuggestionVote).filter(uid == SuggestionVote.SuggestionVote.user_id).filter(row[1].id == SuggestionVote.SuggestionVote.suggestion_id).all()
        single_suggestion["vote_val"] = 0
        if(len(new_q) > 0):
            single_suggestion["vote_val"] = new_q[0].value
        
        
        response_json.append(single_suggestion)
        
    session.close()
    print response_json
    return response_json

def alreadyVoted(u_id, s_id):
    session = Session()
    #first we need to see if there is already a suggestionvote for this user/suggestion combo
    count = session.query(SuggestionVote.SuggestionVote).filter(SuggestionVote.SuggestionVote.suggestion_id == s_id).filter(SuggestionVote.SuggestionVote.user_id == u_id).count()
    return count > 0

def addSuggestionVote(u_id, s_id, amount):
    session = Session()
    suggestion_vote = SuggestionVote.SuggestionVote(value=amount, user_id=u_id, suggestion_id=s_id)
    session.add(suggestion_vote)
    
    q = session.query(Suggestion.Suggestion).filter(s_id == Suggestion.Suggestion.id)
    for row in q:
        row.score = row.score+amount
    
    session.commit()
    session.close()
    
def hasPostedTweetId(twitter_id):
    session = Session()
    #first we need to see if there is already a suggestionvote for this user/suggestion combo
    count = session.query(FBPost.FBPost).filter(FBPost.FBPost.tweet_id == twitter_id).count()
    return count > 0

def postedTweetId(twitter_id):
    session = Session()
    fb_post = FBPost.FBPost(tweet_id=twitter_id)
    session.add(fb_post)
    session.commit()
    session.close()
    
