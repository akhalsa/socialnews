import MySQLdb
import datetime
import re
import urllib2
import Image
import cStringIO
from bs4 import BeautifulSoup

def getTweetWithTwitterId(local_db, twitter_id):
    cursor = local_db.cursor()
    sql = "SELECT  text, blurb, link_url, link_text, img_url, checked FROM Tweet WHERE twitter_id like '"+twitter_id+"';"
    cursor.execute(sql)
    tweet_array = cursor.fetchone()
    tweet_dict ={}
    tweet_dict["id"] = twitter_id
    tweet_dict["text"] = tweet_array[0]
    tweet_dict["blurb"] = tweet_array[1]
    tweet_dict["link_url"] = tweet_array[2]
    tweet_dict["title"] = tweet_array[3]
    tweet_dict["img_url"] = tweet_array[4]
    tweet_dict["checked"] = tweet_array[5]
    cursor.close()    
    return tweet_dict
    
def updateTweet(tweet_text, tweet_id, local_db):
    urls = re.findall('http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', tweet_text)
    if(len(urls) > 0):
        url = urls[0]
        try:
            page_content = urllib2.urlopen(url).read(200000)
        except Exception, e:
            setTweetIdToUnloadable(local_db, tweet_id)
            return
        
        soup = BeautifulSoup(page_content, "html5lib")
        body = soup.find('body')
        
        img_url = ""
        
        if(soup.find("meta", {"property":"og:image"})):
            image_prospect = soup.find("meta", {"property":"og:image"})
            print "there is an image prospect of: "+image_prospect["content"]
            img_url = image_prospect["content"]
            
        else:
            max_area = 0
            for img in body.findAll("img", src=True):
                try:
                    img_file = Image.open(cStringIO.StringIO(urllib2.urlopen(img["src"]).read()))
                    width, height = img_file.size
                    if img.has_attr('height'):
                        float_height = float(img['height'])
                        if(float_height != 0):
                            height = float_height  # set height if site modifies it
                    if img.has_attr('width'):
                        float_width = float(img['width'])
                        if(float_width != 0):
                            width =  float_width # set width if site modifies it
                        
                    area = width*height
                    #if max(width, height) / min(width, height) > 1.5:
                    #    continue
                    
                    if((img["src"].endswith(".gif")) and (area > 10000)):
                        img_url = img["src"]
                        #print "found a gif!!!: "+img["src"]
                        break
                    
                    
                    
                    if(area > max_area):               
                        #print "switching from: "+img_url+" to url:" + img["src"]
                        img_url = img["src"]
                        max_area = area
                        
                except Exception, e:
                    pass
        
        title = u''
        if(soup.find("meta", {"property":"og:title"})):
            title_prospect = soup.find("meta", {"property":"og:title"})
            print "found og:title: "+title_prospect["content"]
            title = title_prospect["content"]
            
        elif(soup.find("meta", {"name":"title"})):
            title_prospect = soup.find("meta", {"name":"title"})
            print "found name:title: "+title_prospect["content"]
            title = title_prospect["content"]

        else:
            for titles in soup.findAll('title'):
                if (titles != tweet_text):
                    title = titles.string
                    break
            
            
        blurb_text = u""
        
        if(soup.find("meta", {"property":"og:description"})):
            blurb_text = soup.find("meta", {"property":"og:description"})["content"]
            print "blurb from og:description: "+blurb_text
        elif(soup.find("meta", {"name": "description"})):
            blurb_text = soup.find("meta", {"name": "description"})["content"]
            print "blurb from name description: "+blurb_text
        
        sql = u"UPDATE Tweet SET blurb=\""+re.escape(blurb_text)
        sql += u"\", link_url=\""+url
        sql += u"\", link_text=\""+re.escape(title)+u"\", "
        sql += "img_url=\""+img_url+"\", checked=1 WHERE twitter_id like '"+tweet_id+"';"
        

        
        insertion_cursor = local_db.cursor()
        try:
                # Execute the SQL command
                insertion_cursor.execute(sql)
                # Commit your changes in the database
                local_db.commit()
        except Exception,e:
                # Rollback in case there is any error
                print "error on update of tweet "
                print str(e)
                local_db.rollback()
        insertion_cursor.close()
    else:
        setTweetIdToUnloadable(local_db, tweet_id)

        
        
def setTweetIdToUnloadable(local_db, tweet_id):
    insertion_cursor = local_db.cursor()
    sql = "UPDATE Tweet SET checked=1 WHERE twitter_id like '"+tweet_id+"';"
    try:
            # Execute the SQL command
            insertion_cursor.execute(sql)
            # Commit your changes in the database
            local_db.commit()
    except Exception,e:
            # Rollback in case there is any error
            print "error on insertion of retweet"
            print str(e)
            local_db.rollback()
    insertion_cursor.close()
    
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
    sql = "select Tweet.twitter_id, Tweet.text, TwitterSource.Name, TwitterSource.profile_image, "
    sql += " Tweet.blurb, Tweet.link_url, Tweet.link_text, Tweet.img_url, Tweet.checked "
    sql += " From Tweet Inner Join TwitterSource ON TwitterSource.twitter_id = Tweet.source_twitter_id WHERE Tweet.twitter_id in ("

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
        for tweet_dict in top_tweets:
            if(tweet_dict["id"] == row[0]):
                tweet_dict["text"] = row[1]
                tweet_dict["name"] = row[2]
                tweet_dict["pic"] = row[3]
                tweet_dict["blurb"] = row[4]
                tweet_dict["link_url"] = row[5]
                tweet_dict["title"] = row[6]
                tweet_dict["img_url"] = row[7]
                tweet_dict["checked"] = row[8]
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

def getAllCategoryIds(local_db):
    cursor = local_db.cursor()
    sql = "SELECT ID FROM Category;"
    cursor.execute(sql)
    cat_id_list = []
    for row in cursor.fetchall() :
        cat_id_list.append(row[0])
    cursor.close()
    return cat_id_list



    
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
    sql = "SELECT VoteHistory.twitter_id, VoteHistory.twitter_handle, VoteHistory.twitter_name, TwitterSource.profile_image, "
    sql += "SUM(value) as vote_count, SUM(case when value >= 0 then value else 0 end) as positive, "
    sql += "SUM(case when value <= 0 then value else 0 end) as negative "
    sql += "From VoteHistory "
    sql += "LEFT JOIN TwitterSource ON VoteHistory.twitter_id=TwitterSource.twitter_id "
    sql += "WHERE category_id like "+str(category_id)+" "
    sql += "GROUP BY VoteHistory.twitter_id ORDER BY vote_count DESC;"
    
    print "will find handles w sql: "+sql
    cursor.execute(sql)
    return_list = []
    insertion_count = 0
    for row in cursor.fetchall() :
        tracked = 1
        if (row[4] <= 0):
                tracked = 0
        
        vote_val = 0
        if(row[0] in user_vote_history):
            vote_val = user_vote_history[row[0]]
            
        return_list.append({"twitter_id": str(row[0]), "vote_val": vote_val, "handle":row[1], "username":row[2], "profile_pic":row[3], "score":str(row[4]),
                            "upvotes": str(row[5]), "downvotes":str(row[6]), "tracked":tracked})
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

def reloadSourceCategoryRelationship(local_db):
    mapping = {}
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
        sql = "INSERT INTO SourceCategoryRelationship (source_twitter_id, category_id) VALUES "
        handle_index = 0
        for vote_record in votes_records:
            if(vote_record[1] <= 0):
                continue
            
            sql += "("+str(vote_record[0])+", "+str(cat_id)+"), "
            
            if vote_record[0] not in mapping:
                mapping[vote_record[0]] = []
            mapping[vote_record[0]].append(cat_id)
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
        
    return mapping
        
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

    




