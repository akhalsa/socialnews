import MySQLdb
import urllib2
import time
from threading import Thread
from src.DBWrapper import *
from tornado.options import define, options, parse_command_line


auth = tweepy.OAuthHandler('pxtsR83wwf0xhKrLbitfIoo5l', 'Z12x1Y7KPRgb1YEWr7nF2UNrVbqEEctj4AiJYFR6J1hDQTXEQK')
auth.set_access_token('24662514-MCXJydvx0Mn5GWfW7RqQmXXsu35m8rNmzxKfHYJcM', 'f6zSrTomKIIr2c5zwcbkpbJYSpAZ2gi40yp57DEd86enN')
api = tweepy.API(auth)


define("mysql_host", default="0", help="Just need the end point", type=int)

host_live = "avtar-news-db-2.cvnwfvvmmyi7.us-west-2.rds.amazonaws.com"
host_dev = "avtar-news-db-dev.cvnwfvvmmyi7.us-west-2.rds.amazonaws.com"
host_target = host_live

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
        
        
def updateSource():
    while True:
        try: 
            local_db_twitter_source = MySQLdb.connect(
                    host=host_target,
                    user="akhalsa",
                    passwd="sophiesChoice1",
                    db="newsdb",
                    charset='utf8',
                    port=3306)
            handle_to_update = fetchOldestHandle(local_db_twitter_source)
            print "***************** GOT TWITTER HANDLE FOR UPDATING  "+str(handle_to_update)
            user = api.get_user(screen_name = handle_to_update)
            user_id = re.escape(str(user.id))
            username = re.escape(user.name)
            profile_link = user.profile_image_url
            updateHandle(local_db_twitter_source, username, user_id, handle_to_update, profile_link)
        except Exception, e:
            print "update exception: "
            print str(e)
            local_db_twitter_source = MySQLdb.connect(
                    host=host_target,
                    user="akhalsa",
                    passwd="sophiesChoice1",
                    db="newsdb",
                    charset='utf8',
                    port=3306)
            ###we dont want to get stuck in a loop on this one broken handle
            handle_to_update = fetchOldestHandle(local_db_twitter_source)
            updateHandle(local_db_twitter_source, "", "", handle_to_update, "")
                
                
        time.sleep(15)
        
def scanPreviews():
    while True:
        local_db_tweets = MySQLdb.connect(
                host=host_target,
                user="akhalsa",
                passwd="sophiesChoice1",
                db="newsdb",
                charset='utf8',
                port=3306)
        all_ids = getAllCategoryIds(local_db_tweets)
        for cat_id in all_ids:
            print "******** Checking: "+str(cat_id)+" *************"
            local_db_tweets = MySQLdb.connect(
                    host=host_target,
                    user="akhalsa",
                    passwd="sophiesChoice1",
                    db="newsdb",
                    charset='utf8',
                    port=3306)
            tweets = getTweetOccurances(900, cat_id, local_db_tweets)
            for tweet in tweets:
                if(tweet["checked"] == 0):
                    print "******** Updating: "+str(tweet["id"])+" *************"
                    print "******** IT IS: "+tweet["text"]
                    try:
                        updateTweet(tweet["text"], tweet["id"], local_db_tweets)
                    except Exception, e:
                        setTweetIdToUnloadable(local_db_tweets, tweet["id"])
            

if __name__ == '__main__':
    parse_command_line()
    if(options.mysql_host == 0):
        host_target = host_live
    elif(options.mysql_host == 1):
        host_target = host_dev
    
    #### start periodic cleaning #####
    worker = Thread(target=periodicClean, args=())
    worker.setDaemon(True)
    worker.start()
    
    ###### start periodic updating of twitter source info #######
    worker = Thread(target=updateSource, args=())
    worker.setDaemon(True)
    worker.start()
    
    ###### start periodic updating of twitter source info #######
    #worker = Thread(target=scanPreviews, args=())
    #worker.setDaemon(True)
    #worker.start()
    
    while True:
        continue
    