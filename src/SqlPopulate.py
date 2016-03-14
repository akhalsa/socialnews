from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
 
engine = create_engine('mysql://akhalsa:sophiesChoice1@avtar-news-db-dev.cvnwfvvmmyi7.us-west-2.rds.amazonaws.com/newsdb', echo=True)
# Bind the engine to the metadata of the Base class so that the
# declaratives can be accessed through a DBSession instance


# create a configured "Session" class
Session = sessionmaker(bind=engine)

# create a Session
session = Session()

# work with sess
myobject = Suggestion("I'm a comment", 2)
session.add(myobject)
session.commit()