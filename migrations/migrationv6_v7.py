from ..src import Suggestion
from ..src import Base

from sqlalchemy import create_engine
from sqlalchemy.orm import relationship, backref, sessionmaker

engine = create_engine('mysql://akhalsa:sophiesChoice1@avtar-news-db-dev.cvnwfvvmmyi7.us-west-2.rds.amazonaws.com/newsdb', echo=True)

def forward():
    Base.Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    session = Session()
    
    
    suggestion = Suggestion.Suggestion(text="first alchemy suggestion", user_id="21")
    session.add(suggestion)
    session.commit()
def backward():
    Suggestion.Suggestion.__table_name__.drop(engine)