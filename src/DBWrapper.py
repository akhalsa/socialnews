import MySQLdb
import datetime
import re

def getTweetOccurances(seconds, cat_id, local_db):
    cursor = local_db.cursor()

    #sql = "SELECT twitter_id as t_id, COUNT(twitter_id) as tweet_occurrence_count FROM TweetOccurrence WHERE timestamp > (NOW() -  INTERVAL "+ str(seconds)+" SECOND) AND category_id like "+str(cat_id)+" GROUP BY twitter_id ORDER BY tweet_occurrence_count DESC LIMIT 10;"
    sql = "SELECT twitter_id as t_id, COUNT(twitter_id) as tweet_occurrence_count FROM Occurrence_"+str(cat_id)+" WHERE timestamp > (NOW() -  INTERVAL "+ str(seconds)+" SECOND) GROUP BY twitter_id ORDER BY tweet_occurrence_count DESC LIMIT 10;"
    print "loading with sql: "+sql
    cursor.execute(sql)
    results = {}
    twitter_ids = []
    top_tweets = []
    for row in cursor.fetchall():
            twitter_ids.append(row[0])
            results[row[0]] = {"tweet_count":row[1] }
            top_tweets.append({"id":row[0], "tweet_count":row[1]})
            
            

    cursor.close()
    #add text
    if(len(twitter_ids)==0):
            return top_tweets
    
    cursor = local_db.cursor()
    sql = "select Tweet.twitter_id, Tweet.text, TwitterSource.Name, TwitterSource.profile_image"
    sql += " Tweet.blurb, Tweet.link_url, Tweet.link_text, Tweet.img_url, Tweet.checked "
    sql+= " From Tweet Inner Join TwitterSource ON TwitterSource.twitter_id = Tweet.source_twitter_id WHERE Tweet.twitter_id in ("
    first_fin = False
    for t_id in twitter_ids:
            if(first_fin == False):
                    first_fin = True
            else:
                    sql +=  ","
                    
            sql += t_id
            
    sql += ");"

    print sql
    cursor.execute(sql)
    for row in cursor.fetchall():
        for tweet_dict in top_tweets:
            if(tweet_dict["id"] == row[0]):
                tweet_dict["text"] = row[1]
                tweet_dict["name"] = row[2]
                tweet_dict["pic"] = row[3]
                if(row[8] == 0):
                    #ok this hasnt been checked.
                    ##so we need to first determine if there is a url
                    ## so lets scan the text for a link first
                    
                    urls = re.findall('http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', tweet_dict["text"])
                    i=0
                    for url in urls:
                        print "found url_"++str(i)+" "+str(url)
                        i += 1
                    
                    


                    ##if there is no link, we can leave everything as null and mark it as checked
                    
                    pass
                else:
                    tweet_dict["blurb"] = row[4]
                    tweet_dict["link_url"] = row[5]
                    tweet_dict["link_text"] = row[6]
                    tweet_dict["img_url"] = row[7]
                    
                break
    cursor.close()
    print top_tweets
    return top_tweets

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
            print "error on insertion of retweet"
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
    if(len(ids_to_check)>0):
        sql = sql[:-2]
    sql += ") GROUP BY twitter_id;"
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
                    print "error on delete from occurrence"
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
        text_string = tweets[tweet]["text"]
        sql += "('"+str(tweets[tweet]["twitter_user_id"])+"', '"+re.escape(text_string)+"', '"+str(tweet)+"'), "
        
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
        print "error into tweets batch"
        print str(e)
        local_db.rollback()
        
    cursor.close()
    
def fetchOldestHandle(local_db):
    cursor = local_db.cursor()
    
    sql = "SELECT * FROM TwitterSource ORDER BY timestamp ASC LIMIT 1"
    cursor.execute(sql)
    handle_id = None
    for row in cursor.fetchall():
        handle_id = row[2]
    cursor.close()
    return handle_id

def updateHandle(local_db, username, user_id, handle, link):
    cursor = local_db.cursor()
    sql = "UPDATE TwitterSource SET Name='"+username+"', twitter_id='"+user_id+"', profile_image='"+link+"', timestamp=CURRENT_TIMESTAMP WHERE twitter_handle='"+handle+"';"
    try:
        # Execute the SQL command
        cursor.execute(sql)
        # Commit your changes in the database
        local_db.commit()
    except Exception,e:
        # Rollback in case there is any error
        print "error on update of twitter source"
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
        print "error on tweet update"
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
    

def getCategoriesWithSourceId(source_id, local_db):
    cursor = local_db.cursor()
    sql = "SELECT category_id FROM SourceCategoryRelationship WHERE source_id like "+str(source_id)+";"
    cursor.execute(sql)
    return_list = []
    for row in cursor.fetchall():
            return_list.append(row[0])
    cursor.close()
    return return_list

def findTableInfoWithTwitterId(twitter_id, local_db):
    cursor = local_db.cursor()
    sql = "SELECT ID, name, twitter_handle, twitter_id FROM TwitterSource WHERE twitter_id like '"+twitter_id+"';"
    cursor.execute(sql)
    return_map = None
    for row in cursor.fetchall() :
        return_map = {}
        return_map ["local_id"] =row[0]
        return_map["twitter_name"] = row[1]
        return_map["twitter_handle"]=row[2]
        return_map["twitter_id"]  = row[3]
        
    cursor.close()
    #print "lock released at 227"
    return return_map

def findTableInfoWithTwitterHandle(twitter_handle, local_db):
    cursor = local_db.cursor()
    sql = "SELECT ID, name, twitter_handle, twitter_id FROM TwitterSource WHERE twitter_handle like '"+twitter_handle+"';"
    cursor.execute(sql)
    return_map = None
    for row in cursor.fetchall() :
        return_map = {}
        return_map ["local_id"] =row[0]
        return_map["twitter_name"] = row[1]
        return_map["twitter_handle"]=row[2]
        return_map["twitter_id"]  = row[3]
        
    cursor.close()
    #print "lock released at 227"
    return return_map

def getCategoryStructure(local_db):
    cursor = local_db.cursor()
    sql = "SELECT * From Category;"
    cursor.execute(sql)
    top = []
    rows = cursor.fetchall()
    cursor.close()
    
    name_map = {}
    full_list = []
    for row in rows:
        name_map[row[0]] = row[1]
        full_list.append(row[0])
    cursor = local_db.cursor()   
    sql = "SELECT * From CategoryParentRelationship;"
    cursor.execute(sql)
    
    
    children_lookup = {}
    for mapping in cursor.fetchall():
        if(mapping[1] not in children_lookup):
            children_lookup[mapping[1]] = []
        children_lookup[mapping[1]].append(mapping[2])
        full_list.remove(mapping[2])
    cursor.close()
    print "generate child lookup: "
    print children_lookup
    
    response = []
    for top_level in full_list:
        response.append(buildMap(name_map,children_lookup, top_level ))
        
    return response
    
def buildMap(id_to_name_map, id_to_children_array_map, id_to_descend):
    output = {}
    output["id"] = id_to_descend
    output["name"] = id_to_name_map[id_to_descend]
    output["children"] = []
    if(id_to_descend in id_to_children_array_map):
        
        for child in id_to_children_array_map[id_to_descend]:
            output["children"].append(buildMap(id_to_name_map, id_to_children_array_map, child))

    return output



def getVoteCountByIpForTimeFrame(local_db, ip_address, seconds):
    cursor = local_db.cursor()
    sql = "SELECT * From VoteHistory WHERE ip_address like '"+ip_address+"' and timestamp > (NOW() -  INTERVAL "+ str(seconds)+" SECOND);"
    cursor.execute(sql)
    votes = cursor.rowcount
    cursor.close()
    return votes

def getAllHandlesForCategory(local_db, category_id, ip_address):
    cursor = local_db.cursor()
    sql = "SELECT value, twitter_id From VoteHistory WHERE ip_address like '"+str(ip_address)+"' AND category_id like '"+str(category_id)+"';"
    cursor.execute(sql)
    user_vote_history = {}
    for row in cursor.fetchall():
        user_vote_history[row[1]] = row[0]
    cursor.close()
    
    cursor = local_db.cursor()
    #note this will get all votes, up or down
    sql = "SELECT twitter_id, twitter_handle, twitter_name, SUM(value) as vote_count From VoteHistory WHERE category_id like "+str(category_id)+" GROUP BY twitter_id ORDER BY vote_count DESC;"
    print "will find handles w sql: "+sql
    cursor.execute(sql)
    return_list = []
    total_nominated_handles = cursor.rowcount
    tracked_handles_count = returnCutOffCount(total_nominated_handles)
    insertion_count = 0
    for row in cursor.fetchall() :
        tracked = 0
        if (insertion_count < tracked_handles_count):
                tracked = 1
        
        vote_val = 0
        if(row[0] in user_vote_history):
            vote_val = user_vote_history[row[0]]
            
        return_list.append({"twitter_id": str(row[0]), "vote_val": vote_val, "handle":row[1], "username":row[2], "score":str(row[3]), "tracked":tracked})
        insertion_count += 1
        
    cursor.close()
    return return_list

def createHandle(local_db, twitter_id, twitter_name, twitter_handle, profile_link):
    cursor = local_db.cursor()
    sql = "INSERT INTO TwitterSource(Name, twitter_handle, twitter_id, profile_image) VALUES ('"+twitter_name+"','"+twitter_handle+"', '"+twitter_id+"', '"+profile_link+"');"
    try:
            # Execute the SQL command
            cursor.execute(sql)
            # Commit your changes in the database
            local_db.commit()
    except Exception,e:
            # Rollback in case there is any error
            print "error on insertion of twitter source"
            print str(e)
            local_db.rollback()
            
    cursor.close()

def returnCutOffCount(total_nominated_handles):
    return max(25, int(total_nominated_handles/2))

def reloadSourceCategoryRelationship(local_db):
    cursor = local_db.cursor()
    sql = "DELETE FROM SourceCategoryRelationship;"
    try:
            # Execute the SQL command
            cursor.execute(sql)
            # Commit your changes in the database
            local_db.commit()
    except Exception,e:
            # Rollback in case there is any error
            print "error on deleting everything from source cat relationship"
            print str(e)
            local_db.rollback()
    cursor.close()
    #### ok source category relationship is flushed
    #### now we need to hit the VotingHistory table to reassemble the source category relationship table
    #logically we should do this category by category
    #need to find top vote getters for each category
    cursor = local_db.cursor()
    sql = "SELECT * From Category;"
    cursor.execute(sql)
    categories = cursor.fetchall()
    cursor.close()
    for row in categories:
        cursor = local_db.cursor()
        cat_id = row[0]
        #simple algorithm... lets just start with the top 30 voted handles ... this may get more complex later
        sql = "SELECT twitter_id, SUM(value) as vote_count FROM VoteHistory WHERE category_id like "+str(cat_id)+" GROUP BY twitter_id ORDER BY vote_count DESC;"
        
        cursor.execute(sql)
        total_nominated_handles = cursor.rowcount
        votes_records = cursor.fetchall()
        cursor.close()
        cursor = local_db.cursor()
        #simple algorithm... lets insert the top 25
        count_tracked_handles = returnCutOffCount(total_nominated_handles)
        handle_index = 0
        sql = "INSERT INTO SourceCategoryRelationship (source_twitter_id, category_id) VALUES "
        
        for vote_record in votes_records:
            if (handle_index == count_tracked_handles):
                break
            sql += "("+str(vote_record[0])+", "+str(cat_id)+"), "
            handle_index += 1
        
        if(handle_index == 0):
            #no votes for anyone in this category...move along
            print "no votes for: "+str(cat_id)
            continue
        
        sql = sql[:-2]
        
        sql += ";"
        try:
            # Execute the SQL command
            cursor.execute(sql)
            # Commit your changes in the database
            local_db.commit()
        except Exception,e:
            # Rollback in case there is any error
            print "error on insertion of source cat relationship"
            print str(e)
            local_db.rollback()
        cursor.close()
        
def getCategoriesForTwitterUserId(local_db, twitter_id):
    cursor = local_db.cursor()
    sql = "SELECT category_id FROM SourceCategoryRelationship WHERE source_twitter_id like "+str(twitter_id)
    cats = []
    cursor.execute(sql)
    for row in cursor.fetchall():
        cats.append(row[0])
    cursor.close()
    return cats
    


def insertVote(local_db, ip_address, category_id, twitter_id, twitter_name, twitter_handle, upvote ):
    cursor = local_db.cursor()
    
    sql = "INSERT INTO VoteHistory(ip_address, category_id, twitter_id, twitter_handle, twitter_name, value) VALUES ('"
    sql += str(ip_address)+"', "+str(category_id)+", "+str(twitter_id)+", '"
    sql += twitter_handle+"', '"+twitter_name+"', "
    sql += "1" if upvote else "-1"
    sql += ");"
    
    try:
            # Execute the SQL command
            cursor.execute(sql)
            # Commit your changes in the database
            local_db.commit()
    except Exception,e:
            # Rollback in case there is any error
            print "error on insertion of vote"
            print str(e)
            local_db.rollback()
    cursor.close()
    return

    




