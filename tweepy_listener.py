import tweepy
import thread
import src.CategoryModel
import time
import urllib2
import datetime
import MySQLdb
import json
import re

from threading import Thread
from Queue import Queue
from tweepy import Stream
from src.DBWrapper import *
from tornado.options import define, options, parse_command_line



auth = tweepy.OAuthHandler('pxtsR83wwf0xhKrLbitfIoo5l', 'Z12x1Y7KPRgb1YEWr7nF2UNrVbqEEctj4AiJYFR6J1hDQTXEQK')
auth.set_access_token('24662514-MCXJydvx0Mn5GWfW7RqQmXXsu35m8rNmzxKfHYJcM', 'f6zSrTomKIIr2c5zwcbkpbJYSpAZ2gi40yp57DEd86enN')
api = tweepy.API(auth)


auth_bot = tweepy.OAuthHandler("1mxHCmJv9pQqFsFO9emtgjrSB", "CcrfJ3WTLqaAigBj0yOhnpAa8bzB6FRG9iIOCVgNktnTgkuHNb")
auth_bot.set_access_token("3618709285-bccgXE7SINoljfJbslsWvP8gP5j9AyQV2FELgIx", "GledD6R46Ghy4dIgtEQBhvW4KfI0n2dN6IUGbWFU2qac2")
api_bot = tweepy.API(auth_bot)

define("mysql_host", default="0", help="Just need the end point", type=int)

host_live = "avtar-news-db-2.cvnwfvvmmyi7.us-west-2.rds.amazonaws.com"
host_dev = "avtar-news-db-dev.cvnwfvvmmyi7.us-west-2.rds.amazonaws.com"
host_target = host_live
    
    


class HandleListener(tweepy.StreamListener):
        
        
        def __init__(self, mdl, refresh):
                self.setupSocket(0)
                self.db_queue = Queue()
                worker = Thread(target=self.handleData, args=())
                worker.setDaemon(True)
                worker.start()
                self.lastClear = datetime.datetime.now() - datetime.timedelta(hours = 1)
                self.lastPost = datetime.datetime.now()
                self.mdl = mdl
                self.refresh_handle_time_seconds = refresh
                
                
        def setupSocketWithDelay(self, delay):
                time.sleep(delay)
                print "starting to set up socket listen on new thread"
                self.kickoff_time = datetime.datetime.now()
                stream = tweepy.Stream(auth, self)
                stream.filter(follow=getAllTwitterIds(db), async=True)

                
        def on_data(self, data):
                self.db_queue.put(data)
                if((datetime.datetime.now() - self.kickoff_time).seconds > self.refresh_handle_time_seconds):
                        thread.start_new_thread( self.setupSocket, (3, ) )
                        return False
                else:
                        return True

        def on_error(self, status):
                print status
                
        def handleData(self,):
            while True:
                data_structure = []
                while(len(data_structure) < 30):
                    data_structure.append(self.db_queue.get())
                
                print "queue size after get: "+str(self.db_queue.qsize())
                self.processBatchData(data_structure)

        
        def processBatchData(self, data_array):
            #must create a map that looks like this:
            # insertion_map = {category_id: [tweet_id,...]}
            # tweet_insertion_map{twitter_id, }
            
            process_start = datetime.datetime.now()
            insertion_map = {}
            unique_ids = {}
            insertion_start = datetime.datetime.now()
            for data in data_array:
                inserted = False
                retweet_insert = False
                decoded = json.loads(data)
                inserted = self.attemptToInsertIntoBatchDictionaty(insertion_map, decoded, unique_ids)
                if(("retweeted_status" in decoded) and (inserted == False)):
                    re_decoded = decoded['retweeted_status']
                    retweet_insert = self.attemptToInsertIntoBatchDictionaty(insertion_map, re_decoded, unique_ids)
            
            print "we had: "+str(len(data_array))+" original rows, and used: "+str(len(unique_ids))+" rows"
            print "spin up time took: "+str((datetime.datetime.now() - insertion_start).total_seconds()) +" seconds"
            ##ok by this point we have a category map that needs to be used to update entries in all categories
            ## we need to do that insertion into the categories and update the tweets table time stampts
            ## tweets table is populated
            ## first run batch insert
            
            insertion_start = datetime.datetime.now()
            batchInsertTweet(unique_ids, db)
            print "tweet insertion time took: "+str((datetime.datetime.now() - insertion_start).total_seconds()) +" seconds"
            
            insertion_start = datetime.datetime.now()
            insertBatch(insertion_map, db)
            print "total insertion time: "+str((datetime.datetime.now() - insertion_start).total_seconds()) +" seconds for: "+str(len(unique_ids))+" records"    
            insertion_start = datetime.datetime.now()
            updateTweetTimeStamp(unique_ids, db)
            print "updating time stamps took: "+str((datetime.datetime.now() - insertion_start).total_seconds()) +" seconds"
            
            print "******** total batch process time: "+str((datetime.datetime.now() - process_start).total_seconds())+" seconds for: "+str(len(unique_ids))+" records" 
            
            
                    
                    
                    
        def attemptToInsertIntoBatchDictionaty(self, batchDictionary, json_object, unique_ids):
            try:
                if(self.mdl.getCategoriesForTwitterUserId(str(json_object['user']['id'])) != None):
                    categories = self.mdl.getCategoriesForTwitterUserId(str(json_object['user']['id']))
                    for cat in categories:
                        if cat not in batchDictionary:
                            batchDictionary[cat] = []
                            
                        batchDictionary[cat].append(json_object['id'])
                                            
                    unique_ids[json_object['id']] = {"twitter_user_id":json_object['user']['id'], "text":json_object['text']}
                    return True
                
            except KeyError, e:
                print "we got a key error so we're just dropping out"
                source_id = 0
                return False
            return False
                                
                                
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
                host=host_target,
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
                host=host_target,
                user="akhalsa",
                passwd="sophiesChoice1",
                db="newsdb",
                charset='utf8',
                port=3306)
        new_tweets = getTweetIdsSince(local_db_surge, 300)
        retweet_targets = getOccurrencesInCategory(local_db_surge, 300, 800, 1, new_tweets)
        if(len(retweet_targets) != 0):
            retweet_targets = getAlreadyRetweeted(retweet_targets, local_db_surge)
            for target in retweet_targets:
                print "should retweet: "+str(target)+" with text: "+new_tweets[target]
                postTweet(new_tweets[target], target)
                insertIntoRetweet(target, True, local_db_surge)
        
        
        local_db_surge.close()


    
if __name__ == '__main__':
        
    parse_command_line()
    if(options.mysql_host == 0):
        host_target = host_live
    elif(options.mysql_host == 1):
        host_target = host_dev
        
    global db

    db = MySQLdb.connect(
        host=host_target,
        user="akhalsa",
        passwd="sophiesChoice1",
        db="newsdb",
        charset='utf8',
        port=3306)
    
    mdl = src.CategoryModel.CategoryModel(db, api)
    
    #### start periodic cleaning #####
    worker = Thread(target=periodicClean, args=())
    worker.setDaemon(True)
    worker.start()
    
    ####### dont check for surges on dev
    if(options.mysql_host == 0):
        ######start periodic surge scanning
        worker_two = Thread(target=periodicSurge, args=())
        worker_two.setDaemon(True)
        worker_two.start()
    
    handle = HandleListener(mdl, 15)
    while True:
        pass

