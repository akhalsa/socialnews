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
import urllib2
import threading
import datetime
import requests
import re
import urllib2

from tornado.options import define, options, parse_command_line
from threading import Thread
from Queue import Queue

define("port", default=8888, help="run on the given port", type=int)

db = MySQLdb.connect(
        host="avtar-news-db-2.cvnwfvvmmyi7.us-west-2.rds.amazonaws.com",
        user="akhalsa",
        passwd="sophiesChoice1",
        db="newsdb",
        charset='utf8',
        port=3306)

lock = threading.Lock()


auth = tweepy.OAuthHandler('pxtsR83wwf0xhKrLbitfIoo5l', 'Z12x1Y7KPRgb1YEWr7nF2UNrVbqEEctj4AiJYFR6J1hDQTXEQK')
auth.set_access_token('24662514-MCXJydvx0Mn5GWfW7RqQmXXsu35m8rNmzxKfHYJcM', 'f6zSrTomKIIr2c5zwcbkpbJYSpAZ2gi40yp57DEd86enN')
api = tweepy.API(auth)


auth_bot = tweepy.OAuthHandler("1mxHCmJv9pQqFsFO9emtgjrSB", "CcrfJ3WTLqaAigBj0yOhnpAa8bzB6FRG9iIOCVgNktnTgkuHNb")
auth_bot.set_access_token("3618709285-bccgXE7SINoljfJbslsWvP8gP5j9AyQV2FELgIx", "GledD6R46Ghy4dIgtEQBhvW4KfI0n2dN6IUGbWFU2qac2")
api_bot = tweepy.API(auth_bot)


                
class HandleListener(tweepy.StreamListener):
        
        def __init__(self):
                thread.start_new_thread( self.setupSocket, ( ) )
                self.db_queue = Queue()
                worker = Thread(target=self.handleData, args=())
                worker.setDaemon(True)
                worker.start()
                self.lastClear = datetime.datetime.now() - datetime.timedelta(hours = 1)
                self.lastPost = datetime.datetime.now()
                
        def setupSocket(self, ):
                print "starting to set up socket listen on new thread"
                auth = tweepy.OAuthHandler('pxtsR83wwf0xhKrLbitfIoo5l', 'Z12x1Y7KPRgb1YEWr7nF2UNrVbqEEctj4AiJYFR6J1hDQTXEQK')
                auth.set_access_token('24662514-MCXJydvx0Mn5GWfW7RqQmXXsu35m8rNmzxKfHYJcM', 'f6zSrTomKIIr2c5zwcbkpbJYSpAZ2gi40yp57DEd86enN')
                stream = tweepy.Stream(auth, self)
                stream.filter(follow=getAllTwitterIds())
                
        def on_data(self, data):
                self.db_queue.put(data)
                return True

        def on_error(self, status):
                print status
                
        def handleData(self,):
                while True:
                        data_structure = self.db_queue.get()
                        #print "queue size after get: "+str(self.db_queue.qsize())
                        insertion_start = datetime.datetime.now()
                        self.processData(data_structure)
                        
                        
                        if((datetime.datetime.now() - self.lastClear).total_seconds() > 900):
                                print "starting to clear entries"
                                clearOldEntries()
                                self.lastClear = datetime.datetime.now()
                        #print "total insertion time: "+str((datetime.datetime.now() - insertion_start).total_seconds()) +" seconds"    
                        self.db_queue.task_done()
                        
        def processData(self, data):
                decoded = json.loads(data)
                #print "recevied: "+str(decoded)
                #check if user for tweet
                #print "scanning: "+str(decoded)

                try:
                        source_id = findTableIdWithTwitterId(str(decoded['user']['id']))
                        #print "done with search tweet user"
                        if(source_id == 0) and ("retweeted_status" in decoded):
                                decoded = decoded['retweeted_status']
                                
                                #print "search retweet user"
                                source_id = findTableIdWithTwitterId(str(decoded['user']['id']))
                                #print "done with search retweet user"
                        elif (source_id == 0):
                                #print "this wasn't a retweet AND wasn't from a trusted source!?!"
                                pass
                        
                except KeyError, e:
                        print "we got a key error so we're just dropping out"
                        source_id = 0
                
                if((source_id != 0) and ('text' in decoded) and ('id' in decoded)):
                        #ok, we have a valid source_id corresponding to the local table_id and decoded holds the right tweet
                        #we need to insert this tweet into the db
                        #first lets check if we already have the tweet
                        local_tweet_id = getLocalTweetIdForTwitterTweetID(decoded['id'])
                        if(local_tweet_id == 0):
                                #print "creating new entry for: "+decoded['text']
                                insertTweet( source_id, decoded['text'], decoded['id'])
                                
                        #print "adding occurance for: "+decoded['text']
                        addOccurance(decoded['id'], source_id)
                        
                        self.checkForSurge(decoded['id'], decoded['text'])
                        
                        
                        if((datetime.datetime.now() - self.lastPost).total_seconds() > 3600):
                                #make sure we are posting at least once an hour
                                (tweet_dict, tweet_ids) = getTweetOccurances(21600, 1)
                                print "got tweet_dict: "+str(tweet_dict)
                                print "and got tweet array: "+str(tweet_ids)
                                
                                for tweet_id in tweet_ids:
                                        if(not checkIfTweeted(tweet_id)):
                                                print "posting: "+str(tweet_id)
                                                postTweet(tweet_dict[tweet_id]["text"], tweet_id)
                                                insertIntoRetweet(tweet_id, False)
                                                #api_bot.retweet(tweet_id)
                                                break
                                        else:
                                                print "would retweet, but we already did"
                                self.lastPost = datetime.datetime.now()
                        
                        #print "finished with: "+decoded['text']
                        
                        
                elif ('text' in decoded):
                        print decoded['text']+ " still had source id that was 0"
                else:
                        print "we had nothing here?"
                        
                        
        def checkForSurge(self, twitter_id, tweet_text):
                lock.acquire()
                cursor = db.cursor()
                sql = "SELECT * From Tweet where twitter_id like '"+str(twitter_id)+"';"
                cursor.execute(sql)
                for row in cursor.fetchall():
                        delta_time = datetime.datetime.now() - row[4]
                cursor.close()
                
                lock.release()
                if(delta_time.total_seconds() < 30):
                        #this is a brand new tweet, lets check the count
                        lock.acquire()
                        cursor = db.cursor()
                        sql = "SELECT * from TweetOccurrence WHERE twitter_id LIKE '"+str(twitter_id)+"' AND timestamp > (NOW() - INTERVAL 30 SECOND);"
                        cursor.execute(sql)
                        occurrence_count = cursor.rowcount
                        cursor.close()
                        lock.release()
                        if(occurrence_count == 150):
                                #api_bot.retweet(twitter_id)
                                postTweet(tweet_text, twitter_id)
                                self.lastPost = datetime.datetime.now()
                                insertIntoRetweet(twitter_id, True)
                                
def postTweet(text, tweet_id):
        urls = re.findall('http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', text)
        if(len(urls) == 0):
                api_bot.retweet(tweet_id)
        else:
                fp = urllib2.urlopen(urls[0])
                if(str(fp.geturl()).startswith("https://twitter.com") or (fp.geturl()).startswith("http://twitter.com")):
                        api_bot.retweet(tweet_id)
                else:
                        api_bot.update_status(status=text)  
        
        
        
def checkIfTweeted(tweet_id):
        print "checking if: "+str(tweet_id)+" has been sent out"
        lock.acquire()
        cursor = db.cursor()
        sql = "SELECT * From Retweets WHERE twitter_id like '"+str(tweet_id)+"';"
        cursor.execute(sql)
        retweet_count = cursor.rowcount
        cursor.close()
        lock.release()
        if(cursor.rowcount > 0):
                return True
        else:
                return False
def insertIntoRetweet(tweet_id, isSurge):
        lock.acquire()
        cursor = db.cursor()
        isSurgeString = "TRUE" if isSurge else "FALSE"
        
        
        sql = "INSERT INTO Retweets (twitter_id, surge) VALUES ('"+str(tweet_id)+"', "+isSurgeString+");"
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
        lock.release()

def clearOldEntries():
        lock.acquire()
        cursor = db.cursor()
        sql = "DELETE FROM TweetOccurrence WHERE timestamp < (NOW() -  INTERVAL 12 HOUR);"
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
        cursor = db.cursor()
        sql = "DELETE FROM Tweet WHERE timestamp < (NOW() -  INTERVAL 12 HOUR);"
        try:
                # Execute the SQL command
                cursor.execute(sql)
                # Commit your changes in the database
                db.commit()
        except Exception,e:
                # Rollback in case there is any error
                print "error on removing uniques of occurrence"
                print str(e)
                db.rollback()
        cursor.close()
        lock.release()
def insertTweet(source_id, text_string, twitter_tweet_id):
        insert_tweet_start = datetime.datetime.now()
        lock.acquire()
        cursor = db.cursor()
        try:
                text_string = text_string.encode('utf-8')
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
        lock.release()
        
        print "insert tweet took: "+str((datetime.datetime.now() - insert_tweet_start).total_seconds())+" seconds" 
        
        
        
def addOccurance(tweet_id, source_id):
        addOccurance_start = datetime.datetime.now()
        local_id = getLocalTweetIdForTwitterTweetID(tweet_id)
        if(local_id == 0):
                return
        
        print "get categories with id: "+str(source_id)
        categories = getCategoriesWithSourceId(source_id)
        
        
        lock.acquire()
        cursor = db.cursor()
        sql = "INSERT INTO TweetOccurrence(twitter_id, category_id) VALUES "
        insert_list = []
        for cat in categories:
            insert_list.append( "('"+str(tweet_id)+"', "+str(cat)+")")
        sql += ",".join(insert_list)
        
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
        #print "addOccurrance took: "+str((datetime.datetime.now() - addOccurance_start).total_seconds())+" seconds" 
        lock.release()


def getLocalTweetIdForTwitterTweetID(twitter_tweet_id):
        lock.acquire()
        cursor = db.cursor()
        sql = "SELECT ID FROM Tweet WHERE twitter_id like "+str(twitter_tweet_id)+";"
        cursor.execute(sql)
        return_id = 0
        for row in cursor.fetchall():
                return_id = row[0]
        cursor.close()
        if(return_id is not 0):
                cursor = db.cursor()
                #we have a valid tweet
                sql = "UPDATE Tweet SET timestamp=NOW() WHERE ID like "+str(twitter_tweet_id)+";"
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
        lock.release()
        return return_id 
def getAllTwitterIds():
        lock.acquire()
        cursor = db.cursor()
        sql = "SELECT twitter_id FROM TwitterSource;"
        cursor.execute(sql)
        return_list = []
        for row in cursor.fetchall():
                return_list.append(row[0])
        cursor.close()
        lock.release()
        return return_list

def getCategoriesWithSourceId(source_id):
        lock.acquire()
        cursor = db.cursor()
        sql = "SELECT category_id FROM SourceCategoryRelationship WHERE source_id like "+str(source_id)+";"
        cursor.execute(sql)
        return_list = []
        for row in cursor.fetchall():
                return_list.append(row[0])
        cursor.close()
        lock.release()
        return return_list
        

def findTableIdWithTwitterId(twitter_id):
        lock.acquire()
        #print "running findTableIdWithTwitterId: "+twitter_id
        cursor = db.cursor()
        sql = "SELECT ID FROM TwitterSource WHERE twitter_id like '"+twitter_id+"';"
        cursor.execute(sql)
        return_id = 0
        for row in cursor.fetchall() :
            return_id = row[0]
        cursor.close()
        #print "lock released at 227"
        lock.release()
        return return_id

def findCategoryChildrenForId(cat_id):
        lock.acquire()
        cursor = db.cursor()
        sql = "SELECT Name From Category WHERE Parent LIKE "+cat_id
        cursor.execute(sql)
        return_list = []
        for row in cursor.fetchall() :
                return_list.append(str(row[0]))
        cursor.close()
        lock.release()
        return return_list

def findCategoryIdWithName(cat_name):
        lock.acquire()
        cursor = db.cursor()
        sql = "SELECT ID FROM Category WHERE Name like '"+cat_name+"';"
        cursor.execute(sql)
        return_id = 0
        for row in cursor.fetchall() :
            return_id = row[0]
        cursor.close()
        lock.release()
        return return_id



def getListOfHandlesForCategoryId(cat_id):
        lock.acquire()
        cursor = db.cursor()
        return_list = []
        sql = "SELECT twitter_id From TwitterSource WHERE ID in (SELECT source_id From SourceCategoryRelationship WHERE category_id="+str(cat_id)+");"
        cursor.execute(sql)
        for row in cursor.fetchall() :
            return_list.append(str(row[0]))
        cursor.close()
        lock.release()
        return return_list

def getTweetOccurances(seconds, cat_id):
        lock.acquire()
        cursor = db.cursor()
        ###
        ## first get tweet occurances filtered for the category we care about
        ####
        #base_string = " AND twitter_id IN (SELECT twitter_id FROM TweetCategoryRelationship WHERE category_id LIKE "+cat_id+")"
        #inner_join = " LEFT JOIN TweetCategoryRelationship On TweetOccurrence.twitter_id=TweetCategoryRelationship.twitter_id"
        #sql = "SELECT twitter_id as t_id, COUNT(twitter_id) as tweet_occurrence_count FROM TweetOccurrence WHERE timestamp > (NOW() -  INTERVAL "+ seconds+" SECOND) GROUP BY twitter_id ORDER BY tweet_occurrence_count DESC "+inner_join
        #sql = "SELECT A.twitter_id, COUNT(A.twitter_id) as tweet_occurrence_count FROM TweetOccurrence A "
        #sql += "INNER JOIN (SELECT twitter_id FROM TweetCategoryRelationship WHERE category_id LIKE "+str(cat_id)+") B "
        #sql += "ON A.twitter_id=B.twitter_id "
        #sql += "WHERE A.timestamp > (NOW() -  INTERVAL "+str(seconds)+" SECOND) GROUP BY A.twitter_id ORDER BY tweet_occurrence_count DESC LIMIT 10"

        sql = "SELECT twitter_id as t_id, COUNT(twitter_id) as tweet_occurrence_count FROM TweetOccurrence WHERE timestamp > (NOW() -  INTERVAL "+ seconds+" SECOND) AND category_id like "+str(cat_id)+" GROUP BY twitter_id ORDER BY tweet_occurrence_count DESC LIMIT 10;"
        
        print "loading with sql: "+sql
        cursor.execute(sql)
        results = {}
        twitter_ids = []
        for row in cursor.fetchall():
                twitter_ids.append(row[0])
                results[row[0]] = {"tweet_count":row[1] }

        cursor.close()
        #add text
        cursor = db.cursor()
        #sql = "SELECT twitter_id, text, source_id From Tweet A "
        #sql += "INNER JOIN (SELECT Name, profile_image, ID FROM TwitterSource) B "
        #sql += "ON A.source = A.source_id "
        #sql += "WHERE A.twitter_id in ("
        sql = "select Tweet.twitter_id, Tweet.text, TwitterSource.Name, TwitterSource.profile_image From Tweet Inner Join TwitterSource ON TwitterSource.ID = Tweet.source_id WHERE Tweet.twitter_id in ("
        first_fin = False
        for t_id in twitter_ids:
                if(first_fin == False):
                        first_fin = True
                else:
                        sql +=  ","
                        
                sql += t_id
                
        sql += ");"

        cursor.execute(sql)
        for row in cursor.fetchall():
                results[row[0]]["text"] = row[1]
                results[row[0]]["name"] = row[2]
                results[row[0]]["pic"] = row[3]
        cursor.close()
        lock.release()
        print results
        return (results, twitter_ids)

class Source(tornado.web.RequestHandler):

    def post(self):
        user_id = False
        username = ""
        profile_link = ""
        for key in self.request.arguments:
            #find the handle
            if(key == "Handle"):
                user = api.get_user(screen_name = self.request.arguments[key][0])
                user_id = str(user.id)
                username = user.name
                profile_link = user.profile_image_url
                print "user_id: "+user_id+" and name: "+username
               
        if(user_id is not False):
            lock.acquire()
            cursor = db.cursor()
            #create user entry
            sql = "INSERT INTO TwitterSource(Name, handle, twitter_id, profile_image) VALUES ('"+username+"','"+self.request.arguments[key][0]+"', '"+user_id+"', '"+profile_link+"')"
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
            lock.release()
            #create relationships to categories
            for key in self.request.arguments:
                print "checking: "+key
                if("cat" in key):
                    
                    cat_id = findCategoryIdWithName(self.request.arguments[key][0])
                    user_db_id = findTableIdWithTwitterId(user_id)
                    lock.acquire()
                    sql = "INSERT INTO SourceCategoryRelationship(source_id, category_id) VALUES ("+str(user_db_id)+", "+str(cat_id)+");"
                    print "inserting category relationships with sql: "+sql
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
                    lock.release()
                    
                else:
                    print "dropping key: "+key
            
            
        else :
            print "no user id found"
        self.finish()
class CategoryChildren(tornado.web.RequestHandler):
    def get(self, cat_label):
        cat_id = findCategoryIdWithName(cat_label)
        children = findCategoryChildrenForId(str(cat_id))
        return_dictionary = {"children":children}
        self.finish(json.dumps(return_dictionary))
        
class Category(tornado.web.RequestHandler):
    def post(self):
        print "attempting to acquire lock at post 384"
        lock.acquire()
        print "successfully acquired lock at post 384"
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
        lock.release()
        self.finish()
        

        
    def get(self, ):
        print "attempting to acquire lock at get 420"
        lock.acquire()
        print "successfully acquired lock at get 420"
        cur = db.cursor()
        cur.execute("SELECT * FROM Category")
        
        output_array = []
        for row in cur.fetchall():
            print ("appending: "+row[1])
            output_map = dict()
            output_map["Name"] = row[1]
            output_array.append(output_map)
        cur.close()
        lock.release()
        self.finish(json.dumps(output_array))
    
class Reader(tornado.web.RequestHandler):
        def get(self, cat, time_frame_seconds):
                print "cat: "+cat
                print "seconds: "+time_frame_seconds
                cat_id = findCategoryIdWithName(cat)
                if(cat_id == 0):
                        self.finish("Category Error, Try Again")
                        
                lookup = getTweetOccurances(time_frame_seconds, str(cat_id))
                self.finish(json.dumps(lookup[0]))
                
class PageLoad(tornado.web.RequestHandler):
        def get(self, url):
                print "********** ATTEMPTING TO ASYNC LOAD: "+url
                self.finish(urllib2.urlopen(url).read(200000))
                

app = tornado.web.Application([
    (r'/static/(.*)', tornado.web.StaticFileHandler, {"path": "./static"}),
    (r"/category", Category),
    (r"/category/(.*)", CategoryChildren),
    (r"/source", Source),
    (r'/reader/(.*)/time/(.*)', Reader),
    (r'/page_load/(.*)',  PageLoad),
])

if __name__ == '__main__':
    parse_command_line()
    #db.query('SET GLOBAL wait_timeout=28800')
    handle = HandleListener()
    
    print "done loading handles"
    app.listen(options.port)
    tornado.ioloop.IOLoop.instance().start()
    
    ####################
    #FIX SQL going away bug
    #http://stackoverflow.com/questions/207981/how-to-enable-mysql-client-auto-re-connect-with-mysqldb
    #####################