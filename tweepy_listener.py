import tweepy
import thread
import src.CategoryModel
import datetime
import MySQLdb
import json

from threading import Thread
from Queue import Queue
from tweepy import Stream

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
                                
                        print "adding occurance for: "+decoded['text']
                        addOccurance(decoded['id'], source_id)
                        
                        self.checkForSurge(decoded['id'], decoded['text'], 1)
                        
                        
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
                        
                        print "finished with: "+decoded['text']
                                                                                          # 
                        
                elif ('text' in decoded):
                        print decoded['text']+ " still had source id that was 0"
                else:
                        print "we had nothing here?"
                        
                        
        def checkForSurge(self, twitter_id, tweet_text, cat_id):
                cursor = db.cursor()
                sql = "SELECT * From Tweet where twitter_id like '"+str(twitter_id)+"';"
                cursor.execute(sql)
                for row in cursor.fetchall():
                        delta_time = datetime.datetime.now() - row[4]
                cursor.close()
                
                if(delta_time.total_seconds() < 300):
                        #this is a brand new tweet, lets check the count
                        cursor = db.cursor()
                        sql = "SELECT * from Occurrence_"+str(cat_id)+" WHERE twitter_id LIKE '"+str(twitter_id)+"' AND timestamp > (NOW() - INTERVAL 300 SECOND);"
                        cursor.execute(sql)
                        occurrence_count = cursor.rowcount
                        cursor.close()
                        if(occurrence_count ==800):
                                #api_bot.retweet(twitter_id)
                                postTweet(tweet_text, twitter_id)
                                self.lastPost = datetime.datetime.now()
                                insertIntoRetweet(twitter_id, True)
                                
                                
def postTweet(text, tweet_id):
    try:
        urls = re.findall('http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', text)
        if(len(urls) == 0):
            api_bot.retweet(tweet_id)
        else:
            fp = urllib2.urlopen(urls[0])
            if(str(fp.geturl()).startswith("https://twitter.com") or (fp.geturl()).startswith("http://twitter.com")):
                    api_bot.retweet(tweet_id)
            else:
                    api_bot.update_status(status=text)
    except Exception, e:
        print "retweet exception: "
        print str(e)
                
        
        
        
def checkIfTweeted(tweet_id):
    print "checking if: "+str(tweet_id)+" has been sent out"
    cursor = db.cursor()
    sql = "SELECT * From Retweets WHERE twitter_id like '"+str(tweet_id)+"';"
    cursor.execute(sql)
    retweet_count = cursor.rowcount
    cursor.close()
    if(cursor.rowcount > 0):
            return True
    else:
            return False
def insertIntoRetweet(tweet_id, isSurge):
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

def clearOldEntries():
    cursor = db.cursor()
    sql = "SELECT ID From Category"
    cursor.execute(sql)
    cats = []
    for row in cursor.fetchall():
            cats.append(row[0])
    cursor.close()
    
    for cat in cats:
            cursor = db.cursor()
            sql = "DELETE From Occurrence_"+str(cat)+" WHERE timestamp < (NOW() -  INTERVAL 12 HOUR);"
            print "Deleting with sql"+sql
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
    
def insertTweet(source_id, text_string, twitter_tweet_id):
    print "inserting tweet: "+text_string
    insert_tweet_start = datetime.datetime.now()
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
    
    print "insert tweet took: "+str((datetime.datetime.now() - insert_tweet_start).total_seconds())+" seconds" 
    
        
def getAllTwitterIds():
        cursor = db.cursor()
        sql = "SELECT twitter_id FROM TwitterSource;"
        cursor.execute(sql)
        return_list = []
        for row in cursor.fetchall():
                return_list.append(row[0])
        cursor.close()
        return return_list
    
    
def addOccurance(tweet_id, source_id):
    addOccurance_start = datetime.datetime.now()
    local_id = getLocalTweetIdForTwitterTweetID(tweet_id)
    if(local_id == 0):
            return
    
    print "get categories with id: "+str(source_id)
    categories = getCategoriesWithSourceId(source_id)
    
    
    cursor = db.cursor()
    for cat in categories:
            sql = "INSERT INTO Occurrence_"+str(cat)+" (twitter_id) VALUES ('"+str(tweet_id)+"');"
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

def findTableIdWithTwitterId(twitter_id):
        #print "running findTableIdWithTwitterId: "+twitter_id
        cursor = db.cursor()
        sql = "SELECT ID FROM TwitterSource WHERE twitter_id like '"+twitter_id+"';"
        cursor.execute(sql)
        return_id = 0
        for row in cursor.fetchall() :
            return_id = row[0]
        cursor.close()
        #print "lock released at 227"
        return return_id
    
if __name__ == '__main__':
    mdl = src.CategoryModel.CategoryModel(db, api)
    handle = HandleListener()
    while True:
        pass

