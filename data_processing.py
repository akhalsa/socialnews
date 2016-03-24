import MySQLdb
import urllib2
import time
import tweepy
from threading import Thread
from src.DBWrapper import *
import facebook
import pprint
from tornado.options import define, options, parse_command_line


auth = tweepy.OAuthHandler('pxtsR83wwf0xhKrLbitfIoo5l', 'Z12x1Y7KPRgb1YEWr7nF2UNrVbqEEctj4AiJYFR6J1hDQTXEQK')
auth.set_access_token('24662514-MCXJydvx0Mn5GWfW7RqQmXXsu35m8rNmzxKfHYJcM', 'f6zSrTomKIIr2c5zwcbkpbJYSpAZ2gi40yp57DEd86enN')
api = tweepy.API(auth)


define("mysql_host", default="0", help="Just need the end point", type=int)

host_live = "avtar-news-db-2.cvnwfvvmmyi7.us-west-2.rds.amazonaws.com"
host_dev = "avtar-news-db-dev.cvnwfvvmmyi7.us-west-2.rds.amazonaws.com"
host_target = host_live


domain_dev = "http://ec2-52-34-7-252.us-west-2.compute.amazonaws.com:8888"
domain_live = "http://filtra.io"
domain_target = domain_live

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
            tweets = getTweetOccurances(900, cat_id, local_db_tweets, 10)
            for tweet in tweets:
                if(tweet["checked"] == 0):
                    print "******** Updating: "+str(tweet["id"])+" *************"
                    try:
                        updateTweet(tweet["text"], tweet["id"], local_db_tweets)
                        print "******** Finished: "+str(tweet["id"])
                    except Exception, e:
                        print "got exception on: "+str(tweet["id"])
                        setTweetIdToUnloadable(local_db_tweets, tweet["id"])
                        
def postNumberOne():
    local_db_fb = MySQLdb.connect(
                host=host_target,
                user="akhalsa",
                passwd="sophiesChoice1",
                db="newsdb",
                charset='utf8',
                port=3306)
    
    target_cat_id = 104
    
    tweets = getTweetOccurances(3600, target_cat_id, local_db_fb, 2)
    
    if(tweets[0]['checked'] == 0):
        try:
            updateTweet(tweets[0]["text"], tweets[0]["id"], local_db_fb)
            print "******** Finished: "+str(tweets[0]["id"])
        except Exception, e:
            print "got exception on: "+str(tweets[0]["id"])
            setTweetIdToUnloadable(local_db_fb, tweets[0]["id"])
            
    tweet = getTweetWithId(local_db_fb, tweets[0]["id"], 1)
    
    img_url = None
    if(tweet["img_url"] is not "") and (tweet["img_url"] is not None):
        img_url = tweet["img_url"]
    else:
        img_url = tweet["profile_image"]
        
    print img_url
    output_text = tweet["twitter_handle"] + " tweets: "+tweet["text"]
    
    filtra_url = domain_target +"/tweet/"+tweets[0]["id"]
    
    attachment =  {
        'name': tweet["twitter_handle"] ,
        'link': filtra_url,
        'description': tweet["text"],
        'caption': 'Filtra - a brief summary of social media',
        
    }
    if(img_url is not None):
        attachment['picture'] = img_url
        
    graph = facebook.GraphAPI(access_token='CAACzgeJoVHgBALjMQAMclitrIPMvdlZBVUtvTLkCaJeqOC2kwRJugqQNRsl0vZBSiizNrhSkEq15tHWZAfBKmYJ9xOcj4FurKnp2A3XP3k5SulX8j5HqBQ3Bl6hf2ZAWz07xbni3ZBQ8KyChlXJThocFXNiR5wSGVNIyNd4nfhlvtidZBmjeZAQ')

    graph.put_wall_post(message=output_text, attachment=attachment, profile_id='1578415282450261')
    


            

if __name__ == '__main__':
    parse_command_line()
    if(options.mysql_host == 0):
        host_target = host_live
        domain_target = domain_live
    elif(options.mysql_host == 1):
        host_target = host_dev
        domain_target = domain_dev
        


    #### start periodic cleaning #####
    worker = Thread(target=periodicClean, args=())
    worker.setDaemon(True)
    #worker.start()
    
    ###### start periodic updating of twitter source info #######
    worker = Thread(target=updateSource, args=())
    worker.setDaemon(True)
    #worker.start()
    
    ###### start periodic updating of twitter source info #######
    worker = Thread(target=scanPreviews, args=())
    worker.setDaemon(True)
    #worker.start()
    
    postNumberOne()
    
    #while True:
    #    continue
    