import MySQLdb
import datetime

def getTweetOccurances(seconds, cat_id, local_db):
    cursor = local_db.cursor()

    #sql = "SELECT twitter_id as t_id, COUNT(twitter_id) as tweet_occurrence_count FROM TweetOccurrence WHERE timestamp > (NOW() -  INTERVAL "+ str(seconds)+" SECOND) AND category_id like "+str(cat_id)+" GROUP BY twitter_id ORDER BY tweet_occurrence_count DESC LIMIT 10;"
    sql = "SELECT twitter_id as t_id, COUNT(twitter_id) as tweet_occurrence_count FROM Occurrence_"+str(cat_id)+" WHERE timestamp > (NOW() -  INTERVAL "+ str(seconds)+" SECOND) GROUP BY twitter_id ORDER BY tweet_occurrence_count DESC LIMIT 10;"
    print "loading with sql: "+sql
    cursor.execute(sql)
    results = {}
    twitter_ids = []
    for row in cursor.fetchall():
            twitter_ids.append(row[0])
            results[row[0]] = {"tweet_count":row[1] }

    cursor.close()
    #add text
    if(len(twitter_ids)==0):
            return (results, twitter_ids)
    
    cursor = local_db.cursor()
    #sql = "SELECT twitter_id, text, source_id From Tweet A "
    #sql += "INNER JOIN (SELECT Name, profile_image, ID FROM TwitterSource) B "
    #sql += "ON A.source = A.source_id "
    #sql += "WHERE A.twitter_id in ("
    sql = "select Tweet.twitter_id, Tweet.text, TwitterSource.Name, TwitterSource.profile_image From Tweet Inner Join TwitterSource ON TwitterSource.twitter_id = Tweet.source_twitter_id WHERE Tweet.twitter_id in ("
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
    print results
    return (results, twitter_ids)

def findCategoryIdWithName(cat_name, local_db):
    cursor = local_db.cursor()
    sql = "SELECT ID FROM Category WHERE Name like '"+cat_name+"';"
    cursor.execute(sql)
    return_id = 0
    for row in cursor.fetchall() :
        return_id = row[0]
    cursor.close()
    return return_id

def findCategoryChildrenForId(cat_id, local_db):
    cursor = local_db.cursor()
    sql = "SELECT child_category_id From CategoryParentRelationship WHERE parent_category_id LIKE "+cat_id
    cursor.execute(sql)
    child_id_list = []
    for row in cursor.fetchall() :
            child_id_list.append(str(row[0]))
    cursor.close()
    
    cursor = local_db.cursor()
    return_list = []
    for id in child_id_list:
            sql = "SELECT Name From Category WHERE ID like "+id
            cursor.execute(sql)
            row = cursor.fetchone()
            return_list.append(str(row[0]))
    cursor.close()
    return return_list

def checkIfTweeted(tweet_id, local_db):
    print "checking if: "+str(tweet_id)+" has been sent out"
    cursor = local_db.cursor()
    sql = "SELECT * From Retweets WHERE twitter_id like '"+str(tweet_id)+"';"
    cursor.execute(sql)
    retweet_count = cursor.rowcount
    cursor.close()
    if(cursor.rowcount > 0):
        return True
    else:
        return False
    
def insertIntoRetweet(tweet_id, isSurge, local_db):
    cursor = local_db.cursor()
    isSurgeString = "TRUE" if isSurge else "FALSE"
    
    
    sql = "INSERT INTO Retweets (twitter_id, surge) VALUES ('"+str(tweet_id)+"', "+isSurgeString+");"
    try:
            # Execute the SQL command
            cursor.execute(sql)
            # Commit your changes in the database
            local_db.commit()
    except Exception,e:
            # Rollback in case there is any error
            print "error on insertion of occurrence"
            print str(e)
            local_db.rollback()
    cursor.close()
    
def getAlreadyRetweeted(tweet_id_list, local_db):
    sql = "SELECT twitter_id From Retweets WHERE twitter_id IN ("
    for t_id in tweet_id_list:
        sql += "'"+str(t_id)+"', "
    if(len(tweet_id_list)>0):
        sql = sql[:-2]
    sql += ");"
    cursor = local_db.cursor()
    cursor.execute(sql)
    for row in cursor.fetchall():
        if(row[0] in tweet_id_list):
            tweet_id_list.remove(row[0])
    return tweet_id_list


def getTweetIdsSince(local_db, seconds_delta):
    cursor = local_db.cursor()
    sql = "SELECT twitter_id, text from Tweet WHERE insertion_timestamp > (NOW() - INTERVAL "+str(seconds_delta)+" SECOND);"
    print "using sql: "+sql+" to select new tweets"
    cursor.execute(sql)
    return_twitter_ids = {}
    for row in cursor.fetchall():
        return_twitter_ids[row[0]] = row[1]
    cursor.close()
    return return_twitter_ids
    
def getOccurrencesInCategory(local_db, seconds_delta, threshold, category_id, ids_to_check):
    sql = "SELECT twitter_id as t_id, COUNT(twitter_id) as tweet_occurrence_count FROM Occurrence_"+str(category_id)+" WHERE timestamp > (NOW() - INTERVAL "+str(seconds_delta)+" SECOND) "
    sql += "AND twitter_id IN ("
    
    for t_id in ids_to_check:
        sql += "'"+str(t_id)+"', "
    
    sql = sql[:-2]
    sql += ") GROUP BY twitter_id;"
    print "will execute sql: "+sql
    cursor = local_db.cursor()
    cursor.execute(sql)
    return_twitter_ids = []
    for row in cursor.fetchall():
        if(row[1] > threshold):
            return_twitter_ids.append(row[0])
    cursor.close()
    return return_twitter_ids
    

    
    

def clearOldEntries(local_db):
    cursor = local_db.cursor()
    sql = "SELECT ID From Category"
    cursor.execute(sql)
    cats = []
    for row in cursor.fetchall():
            cats.append(row[0])
    cursor.close()
    
    for cat in cats:
            cursor = local_db.cursor()
            sql = "DELETE From Occurrence_"+str(cat)+" WHERE timestamp < (NOW() -  INTERVAL 12 HOUR);"
            print "Deleting with sql"+sql
            try:
                    # Execute the SQL command
                    cursor.execute(sql)
                    # Commit your changes in the database
                    local_db.commit()
            except Exception,e:
                    # Rollback in case there is any error
                    print "error on insertion of occurrence"
                    print str(e)
                    local_db.rollback()
            cursor.close()
    cursor = local_db.cursor()
    sql = "DELETE FROM Tweet WHERE timestamp < (NOW() -  INTERVAL 12 HOUR);"
    try:
            # Execute the SQL command
            cursor.execute(sql)
            # Commit your changes in the database
            local_db.commit()
    except Exception,e:
            # Rollback in case there is any error
            print "error on removing uniques of occurrence"
            print str(e)
            local_db.rollback()
    cursor.close()

def insertTweet(source_id, text_string, twitter_tweet_id, local_db):
    insert_tweet_start = datetime.datetime.now()
    cursor = local_db.cursor()
    try:
            text_string = text_string.encode('utf-8')
            sql = "INSERT INTO Tweet(source_twitter_id, text, twitter_id) VALUES ("+str(source_id)+",'"+MySQLdb.escape_string(text_string)+"', '"+str(twitter_tweet_id)+"');"
            # Execute the SQL command
            cursor.execute(sql)
            # Commit your changes in the database
            local_db.commit()
    except Exception,e:
            # Rollback in case there is any error
            print "error on Tweet insertion"
            print str(e)
            local_db.rollback()
    cursor.close()
    
    
def getAllTwitterIds(local_db):
    cursor = local_db.cursor()
    sql = "SELECT twitter_id FROM TwitterSource;"
    cursor.execute(sql)
    return_list = []
    for row in cursor.fetchall():
            return_list.append(row[0])
    cursor.close()
    return return_list


def insertBatch(insertion_map, local_db):
    ##insertion_map = {category_id: [tweet_id,...]}
    cursor = local_db.cursor()
    try:
        for cat in insertion_map:
            sql = "INSERT INTO Occurrence_"+str(cat)+" (twitter_id) VALUES "
            for tweet_id in insertion_map[cat]:
                sql += "('"+str(tweet_id)+"'), "
            sql = sql[:-2]
            sql+="; "
            cursor.execute(sql)
        local_db.commit()
    except Exception,e:
        # Rollback in case there is any error
        print "error on insertion of occurrence"
        print str(e)
        local_db.rollback()
        sys.exit()
        
    cursor.close()
    
def batchInsertTweet(tweets, local_db):
    sql ="INSERT IGNORE INTO Tweet(source_twitter_id, text, twitter_id) VALUES "
    for tweet in tweets:
        text_string = tweets[tweet]["text"].encode('utf-8')
        sql += "('"+str(tweets[tweet]["twitter_user_id"])+"', '"+MySQLdb.escape_string(text_string)+"', '"+str(tweet)+"'), "
        
    if(len(tweets)>0):
        sql = sql[:-2]
    
    cursor = local_db.cursor()
    try:
        # Execute the SQL command
        cursor.execute(sql)
        # Commit your changes in the database
        local_db.commit()
    except Exception,e:
        # Rollback in case there is any error
        print "error on insertion of occurrence"
        print str(e)
        local_db.rollback()
        
    cursor.close()
    

    

def updateTweetTimeStamp(tweet_list, local_db):
    if (len(tweet_list) == 0):
        return
    
    sql = "UPDATE Tweet set timestamp=CURRENT_TIMESTAMP WHERE twitter_id IN ("
    for tweet_id in tweet_list:
        sql += "'"+str(tweet_id)+"', "
        
    sql = sql[:-2]
    sql +=");"
    cursor = local_db.cursor()
    try:
        # Execute the SQL command
        cursor.execute(sql)
        # Commit your changes in the database
        local_db.commit()
    except Exception,e:
        # Rollback in case there is any error
        print "error on insertion of occurrence"
        print str(e)
        local_db.rollback()
        
    cursor.close()
    
    
    

def addOccurance(tweet_id, source_id, local_db):
    addOccurance_start = datetime.datetime.now()
    local_id = getLocalTweetIdForTwitterTweetID(tweet_id, local_db)
    if(local_id == 0):
            return
    
    print "get categories with id: "+str(source_id)
    categories = getCategoriesWithSourceId(source_id, local_db)
    
    
    cursor = local_db.cursor()
    for cat in categories:
            sql = "INSERT INTO Occurrence_"+str(cat)+" (twitter_id) VALUES ('"+str(tweet_id)+"');"
            try:
                    # Execute the SQL command
                    cursor.execute(sql)
                    # Commit your changes in the database
                    local_db.commit()
            except Exception,e:
                    # Rollback in case there is any error
                    print "error on insertion of occurrence"
                    print str(e)
                    local_db.rollback()
            
    cursor.close()
    #print "addOccurrance took: "+str((datetime.datetime.now() - addOccurance_start).total_seconds())+" seconds"
    
def getLocalTweetIdForTwitterTweetID(twitter_tweet_id, local_db):
    cursor = local_db.cursor()
    sql = "SELECT ID FROM Tweet WHERE twitter_id like "+str(twitter_tweet_id)+";"
    cursor.execute(sql)
    return_id = 0
    for row in cursor.fetchall():
            return_id = row[0]
    cursor.close()
    if(return_id is not 0):
            cursor = local_db.cursor()
            #we have a valid tweet
            sql = "UPDATE Tweet SET timestamp=NOW() WHERE ID like "+str(twitter_tweet_id)+";"
            try:
                    # Execute the SQL command
                    cursor.execute(sql)
                    # Commit your changes in the database
                    local_db.commit()
            except Exception,e:
                    # Rollback in case there is any error
                    print "error on insertion of occurrence"
                    print str(e)
                    local_db.rollback()
    cursor.close()
    return return_id

def getCategoriesWithSourceId(source_id, local_db):
    cursor = local_db.cursor()
    sql = "SELECT category_id FROM SourceCategoryRelationship WHERE source_id like "+str(source_id)+";"
    cursor.execute(sql)
    return_list = []
    for row in cursor.fetchall():
            return_list.append(row[0])
    cursor.close()
    return return_list

def findTableIdWithTwitterId(twitter_id, local_db):
    cursor = local_db.cursor()
    sql = "SELECT ID FROM TwitterSource WHERE twitter_id like '"+twitter_id+"';"
    cursor.execute(sql)
    return_id = 0
    for row in cursor.fetchall() :
        return_id = row[0]
    cursor.close()
    #print "lock released at 227"
    return return_id

