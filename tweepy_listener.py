import tweepy
import thread
import src.CategoryModel
import time

import datetime
import MySQLdb
import json
import re

from threading import Thread
from Queue import Queue
from tweepy import Stream
from src.DBWrapper import *

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
        
        def __init__(self, mdl):
                thread.start_new_thread( self.setupSocket, ( ) )
                self.db_queue = Queue()
                worker = Thread(target=self.handleData, args=())
                worker.setDaemon(True)
                worker.start()
                self.lastClear = datetime.datetime.now() - datetime.timedelta(hours = 1)
                self.lastPost = datetime.datetime.now()
                self.mdl = mdl
                
        def setupSocket(self, ):
                print "starting to set up socket listen on new thread"
                stream = tweepy.Stream(auth, self)
                stream.filter(follow=getAllTwitterIds(db))

                
        def on_data(self, data):
                self.db_queue.put(data)
                return True

        def on_error(self, status):
                print status
                
        def handleData(self,):
            while True:
                data_structure = []
                while(len(data_structure) < 10):
                    data_structure.append(self.db_queue.get())
                
                print "queue size after get: "+str(self.db_queue.qsize())
                self.processBatchData(data_structure)

        
        def processBatchData(self, data_array):
            #must create a map that looks like this:
            # insertion_map = {category_id: [tweet_id,...]}
            # tweet_insertion_map{twitter_id, }
            
            
            insertion_map = {}
            unique_ids = {}
            for data in data_array:
                decoded = json.loads(data)
                self.attemptToInsertIntoBatchDictionaty(insertion_map, decoded, unique_ids)
                if("retweeted_status" in decoded):
                    decoded = decoded['retweeted_status']
                    self.attemptToInsertIntoBatchDictionaty(insertion_map, decoded, unique_ids)
            
            ##ok by this point we have a category map that needs to be used to update entries in all categories
            ## we need to do that insertion into the categories and update the tweets table time stampts
            ## tweets table is populated
            ## first run batch insert
            insertion_start = datetime.datetime.now()
            insertBatch(insertion_map, db)
            print "total insertion time: "+str((datetime.datetime.now() - insertion_start).total_seconds()) +" seconds for: "+str(len(unique_ids))+" records"    
            insertion_start = datetime.datetime.now()
            updateTweetTimeStamp(unique_ids, db)
            print "updating time stamps took: "+str((datetime.datetime.now() - insertion_start).total_seconds()) +" seconds"
            
            
            
            
                    
                    
                    
        def attemptToInsertIntoBatchDictionaty(self, batchDictionary, json_object, unique_ids):
            try:
                if(self.mdl.getCategoriesForTwitterUserId(str(json_object['user']['id'])) != None):
                    categories = self.mdl.getCategoriesForTwitterUserId(str(json_object['user']['id']))
                    for cat in categories:
                        if cat not in batchDictionary:
                            batchDictionary[cat] = []
                            
                        batchDictionary[cat].append(json_object['id'])
                        
                    #local_tweet_id = getLocalTweetIdForTwitterTweetID(json_object['id'], db)
                    #if(local_tweet_id == 0):
                    print "creating new entry for: "+json_object['text']
                    insertTweet( json_object['user']['id'], json_object['text'], json_object['id'], db)
                    unique_ids[json_object['id']] = True 
                
            except KeyError, e:
                print "we got a key error so we're just dropping out"
                source_id = 0
                
                



                            
        def processData(self, data):
                decoded = json.loads(data)
                #print "recevied: "+str(decoded)
                #check if user for tweet
                #print "scanning: "+str(decoded)

                try:
                        source_id = findTableIdWithTwitterId(str(decoded['user']['id']), db)
                        #print "done with search tweet user"
                        if(source_id == 0) and ("retweeted_status" in decoded):
                                decoded = decoded['retweeted_status']
                                
                                #print "search retweet user"
                                source_id = findTableIdWithTwitterId(str(decoded['user']['id']), db)
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
                        local_tweet_id = getLocalTweetIdForTwitterTweetID(decoded['id'], db)
                        if(local_tweet_id == 0):
                                #print "creating new entry for: "+decoded['text']
                                insertTweet( source_id, decoded['text'], decoded['id'], db)
                                
                        print "adding occurance for: "+decoded['text']
                        addOccurance(decoded['id'], source_id, db)
                        
                        self.checkForSurge(decoded['id'], decoded['text'], 1)
                        
                        
                        if((datetime.datetime.now() - self.lastPost).total_seconds() > 3600):
                                #make sure we are posting at least once an hour
                                (tweet_dict, tweet_ids) = getTweetOccurances(21600, 1, db)
                                print "got tweet_dict: "+str(tweet_dict)
                                print "and got tweet array: "+str(tweet_ids)
                                
                                for tweet_id in tweet_ids:
                                        if(not checkIfTweeted(tweet_id, db)):
                                                print "posting: "+str(tweet_id)
                                                postTweet(tweet_dict[tweet_id]["text"], tweet_id)
                                                insertIntoRetweet(tweet_id, False, db)
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
                                insertIntoRetweet(twitter_id, True, db)
                                
                                
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
             
def periodicClean():
    while True:
        local_db_clean = MySQLdb.connect(
                host="avtar-news-db-2.cvnwfvvmmyi7.us-west-2.rds.amazonaws.com",
                user="akhalsa",
                passwd="sophiesChoice1",
                db="newsdb",
                charset='utf8',
                port=3306)
        clearOldEntries(local_db_clean)
        local_db_clean.close()
        time.sleep(900)
        
def periodicSurge():
    while True:
        time.sleep(30)
        local_db_surge = MySQLdb.connect(
                host="avtar-news-db-2.cvnwfvvmmyi7.us-west-2.rds.amazonaws.com",
                user="akhalsa",
                passwd="sophiesChoice1",
                db="newsdb",
                charset='utf8',
                port=3306)
        new_tweets = getTweetIdsSince(local_db_surge, 300)
        print "new tweets are: "+str(new_tweets)
        retweet_targets = getOccurrencesInCategory(local_db_surge, 300, 50, 1, new_tweets)
        retweet_targets = getAlreadyRetweeted(retweet_targets, local_db_surge)
        for target in retweet_targets:
            print "should retweet: "+str(target)+" with text: "+new_tweets[target]
            postTweet(new_tweets[target], target)
            insertIntoRetweet(target, True, local_db_surge)
        
        
        local_db_surge.close()

    
if __name__ == '__main__':
    mdl = src.CategoryModel.CategoryModel(db, api)
    
    #### start periodic cleaning #####
    # worker = Thread(target=periodicClean, args=())
    # worker.setDaemon(True)
    # worker.start()
    
    ######start periodic surge scanning
    # worker_two = Thread(target=periodicSurge, args=())
    # worker_two.setDaemon(True)
    # worker_two.start()
    
    handle = HandleListener(mdl)
    while True:
        pass

