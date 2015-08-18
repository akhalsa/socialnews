import tornado.ioloop
import tornado.web
import tornado.websocket
import os, uuid
import socket   #for sockets
import sys  #for exit
import json
import MySQLdb
import tweepy
import thread

from tornado.options import define, options, parse_command_line
from threading import Thread

define("port", default=8888, help="run on the given port", type=int)

db = MySQLdb.connect(
        host="avtar-news-db-2.cvnwfvvmmyi7.us-west-2.rds.amazonaws.com",
        user="akhalsa",
        passwd="sophiesChoice1",
        db="newsdb",
        charset='utf8',
        port=3306)


auth = tweepy.OAuthHandler('pxtsR83wwf0xhKrLbitfIoo5l', 'Z12x1Y7KPRgb1YEWr7nF2UNrVbqEEctj4AiJYFR6J1hDQTXEQK')
auth.set_access_token('24662514-MCXJydvx0Mn5GWfW7RqQmXXsu35m8rNmzxKfHYJcM', 'f6zSrTomKIIr2c5zwcbkpbJYSpAZ2gi40yp57DEd86enN')
api = tweepy.API(auth)

                
class HandleListener(tweepy.StreamListener):
        def __init__(self):
                thread.start_new_thread( self.setupSocket, ( ) )

                
        def setupSocket(self, ):
                print "starting to set up socket listen on new thread"
                auth = tweepy.OAuthHandler('pxtsR83wwf0xhKrLbitfIoo5l', 'Z12x1Y7KPRgb1YEWr7nF2UNrVbqEEctj4AiJYFR6J1hDQTXEQK')
                auth.set_access_token('24662514-MCXJydvx0Mn5GWfW7RqQmXXsu35m8rNmzxKfHYJcM', 'f6zSrTomKIIr2c5zwcbkpbJYSpAZ2gi40yp57DEd86enN')
                stream = tweepy.Stream(auth, self)
                stream.filter(follow=getAllTwitterIds())
                
        def on_data(self, data):
                decoded = json.loads(data)
                #print "recevied: "+str(decoded)
                #check if user for tweet
                source_id = findTableIdWithTwitterId(str(decoded['user']['id']))
                if(source_id == 0) and ("retweeted_status" in decoded):
                        decoded = decoded['retweeted_status']
                        source_id = findTableIdWithTwitterId(str(decoded['user']['id']))
                elif (source_id == 0):
                        print "this wasn't a retweet AND wasn't from a trusted source!?!"
                
                
                if(source_id != 0):
                        #ok, we have a valid source_id corresponding to the local table_id and decoded holds the right tweet
                        #we need to insert this tweet into the db
                        #first lets check if we already have the tweet
                        local_tweet_id = getLocalTweetIdForTwitterTweetID(decoded['id'])
                        if(local_tweet_id == 0):
                                print "creating new entry for: "+decoded['text']
                                insertTweet( source_id, decoded['text'], decoded['id'])
                                
                        print "adding occurance for: "+decoded['text']
                        addOccurance(decoded['id'])
                else:
                        print "source id was still 0 ... so trusted source to be found"
                
                
                return True

        def on_error(self, status):
                print status


def insertTweet(source_id, text_string, twitter_tweet_id):
        cursor = db.cursor()
        try:
                sql = "INSERT INTO Tweet(source_id, text, twitter_id) VALUES ("+str(source_id)+",'"+MySQLdb.escape_string(text_string)+"', '"+str(twitter_tweet_id)+"');"
                # Execute the SQL command
                cursor.execute(sql)
                # Commit your changes in the database
                db.commit()
        except Exception,e:
                # Rollback in case there is any error
                print "error on Tweet insertion"
                print str(e)
                db.rollback()
        cursor.close()
        print "get categories with id: "+str(source_id)
        categories = getCategoriesWithSourceId(source_id)
        cursor = db.cursor()
        for cat in categories:
                print "should insert category relationship to cat_id: "+str(cat)
                sql = "INSERT INTO TweetCategoryRelationship(twitter_id, category_id) VALUES ('"+str(twitter_tweet_id)+"',"+str(cat)+");"
                try:
                        # Execute the SQL command
                        cursor.execute(sql)
                        # Commit your changes in the database
                        db.commit()
                except Exception,e:
                        # Rollback in case there is any error
                        print "error on TweetCat update"
                        print str(e)
                        db.rollback()
        
        cursor.close()
        
        
        
def addOccurance(tweet_id):
        cursor = db.cursor()
        sql = "INSERT INTO TweetOccurrence(twitter_id) VALUES ('"+str(tweet_id)+"');"
        try:
                # Execute the SQL command
                cursor.execute(sql)
                # Commit your changes in the database
                db.commit()
        except Exception,e:
                # Rollback in case there is any error
                print "error on insertion of occurrence"
                print str(e)
                db.rollback()
        cursor.close()

def getLocalTweetIdForTwitterTweetID(twitter_tweet_id):
        cursor = db.cursor()
        sql = "SELECT ID FROM Tweet WHERE twitter_id like "+str(twitter_tweet_id)+";"
        cursor.execute(sql)
        return_id = 0
        for row in cursor.fetchall():
                return_id = row[0]
        cursor.close()
        return return_id 
def getAllTwitterIds():
        cursor = db.cursor()
        sql = "SELECT twitter_id FROM TwitterSource;"
        cursor.execute(sql)
        return_list = []
        for row in cursor.fetchall():
                return_list.append(row[0])
        cursor.close()
        return return_list

def getCategoriesWithSourceId(source_id):
        cursor = db.cursor()
        sql = "SELECT category_id FROM SourceCategoryRelationship WHERE source_id like "+str(source_id)+";"
        cursor.execute(sql)
        return_list = []
        for row in cursor.fetchall():
                return_list.append(row[0])
        cursor.close()
        return return_list
        

def findTableIdWithTwitterId(twitter_id):
        cursor = db.cursor()
        sql = "SELECT ID FROM TwitterSource WHERE twitter_id like '"+twitter_id+"';"
        cursor.execute(sql)
        return_id = 0
        for row in cursor.fetchall() :
            return_id = row[0]
        cursor.close()    
        return return_id


def findCategoryIdWithName(cat_name):
    cursor = db.cursor()
    sql = "SELECT ID FROM Category WHERE Name like '"+cat_name+"';"
    cursor.execute(sql)
    return_id = 0
    for row in cursor.fetchall() :
        return_id = row[0]
    cursor.close()    
    return return_id



def getListOfHandlesForCategoryId(cat_id):
    cursor = db.cursor()
    return_list = []
    sql = "SELECT twitter_id From TwitterSource WHERE ID in (SELECT source_id From SourceCategoryRelationship WHERE category_id="+str(cat_id)+");"
    cursor.execute(sql)
    for row in cursor.fetchall() :
        return_list.append(str(row[0]))
    cursor.close()
    return return_list

def getTweetOccurances():
        cursor = db.cursor()
        sql = "SELECT twitter_id as t_id, COUNT(twitter_id) as tweet_occurrence_count FROM TweetOccurrence GROUP BY twitter_id ORDER BY tweet_occurrence_count DESC LIMIT 10;"
        cursor.execute(sql)
        results = {}
        twitter_ids = []
        for row in cursor.fetchall():
                twitter_ids.append(row[0])
                results[row[0]] = (row[1], )
        cursor.close()
        #add text
        cursor = db.cursor()
        sql = "SELECT twitter_id, text From Tweet WHERE twitter_id in ("
        for t_id in twitter_ids:
               sql += t_id+","
        sql += ");"
        print "will get text with sql: "+sql
        return results

class Source(tornado.web.RequestHandler):

    def post(self):
        
        user_id = False
        username = ""
        for key in self.request.arguments:
            #find the handle
            if(key == "Handle"):
                user = api.get_user(screen_name = self.request.arguments[key][0])
                user_id = str(user.id)
                username = user.name
                print "user_id: "+user_id+" and name: "+username
               
        if(user_id is not False):
            cursor = db.cursor()
            #create user entry
            sql = "INSERT INTO TwitterSource(Name, handle, twitter_id) VALUES ('"+username+"','"+self.request.arguments[key][0]+"', '"+user_id+"')"
            try:
                # Execute the SQL command
                cursor.execute(sql)
                # Commit your changes in the database
                db.commit()
            except:
                # Rollback in case there is any error
                print "error on insertion"
                db.rollback()
            cursor.close()
            
            #create relationships to categories
            for key in self.request.arguments:
                if("cat" in key):
                    
                    cat_id = findCategoryIdWithName(self.request.arguments[key][0])
                    user_db_id = findTableIdWithTwitterId(user_id)
                    sql = "INSERT INTO SourceCategoryRelationship(source_id, category_id) VALUES ("+str(user_db_id)+", "+str(cat_id)+");"
                    cursor = db.cursor()
                    try:
                        # Execute the SQL command
                        cursor.execute(sql)
                        # Commit your changes in the database
                        db.commit()
                    except:
                        # Rollback in case there is any error
                        print "error on insertion"
                        db.rollback()
                    cursor.close()
                    
                else:
                    print "dropping key: "+key
            
            
        else :
            print "no user id found"
        self.finish()
        
class Category(tornado.web.RequestHandler):
    def post(self):
        title = self.get_argument('Title', '')
        parent_cat = self.get_argument('parent', '')
        cursor = db.cursor()
        #first locate the ID if there is one of the parent Category
        sql = """SELECT ID From Category WHERE Name Like '"""+parent_cat+"""';""";
        cursor.execute(sql)
        
        new_id = "NULL"
        for row in cursor.fetchall() :
            new_id = row[0]
        
        
        
        sql = "INSERT INTO Category(Name, Parent) VALUES ('"+title+"', "+str(new_id)+")"
        print "inserting with: "+sql
        
        try:
            # Execute the SQL command
            cursor.execute(sql)
            # Commit your changes in the database
            db.commit()
        except:
            # Rollback in case there is any error
            print "error on insertion"
            db.rollback()
            
        cursor.close()
        self.finish()
        
    def get(self, id):
        print "running get with id: "+str(id)
        self.finish()
        
    def get(self, ):
        cur = db.cursor()
        cur.execute("SELECT * FROM Category")
        
        output_array = []
        for row in cur.fetchall():
            print ("appending: "+row[1])
            output_map = dict()
            output_map["Name"] = row[1]
            output_array.append(output_map)
        cur.close()
        self.finish(json.dumps(output_array))
    
class Reader(tornado.web.RequestHandler):
        def get(self, time_frame_seconds):
                lookup = getTweetOccurances()
                print "found results"
                print lookup
                self.finish("loaded with time: "+str(time_frame_seconds))
                
        

app = tornado.web.Application([
    (r'/static/(.*)', tornado.web.StaticFileHandler, {"path": "./static"}),
    (r"/category", Category),
    (r"/source", Source),
    (r'/reader/(.*)', Reader),
])

if __name__ == '__main__':
    parse_command_line()
    handle = HandleListener()
    ##############################
    # Note: this approach does not work. you need to set up a single stream for ALL handles we care about
    # Then for each incoming tweet, we want to look at the text, and determine categories by looking for a known handle in the id OR retweeted id
    # This can be done using a hash lookup for big O of 1 instead of N as this operation will be done very frequently
    # This approach will require a system reboot each time new handles get added
    # this is probably not the end of the world for now
    ##############################
    
    print "done loading handles"
    app.listen(options.port)
    tornado.ioloop.IOLoop.instance().start()