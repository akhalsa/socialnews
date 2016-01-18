import MySQLdb


def clearConversationsForCategoryId(db, category_id):
    conversation_id = None
    cursor = db.cursor()
    sql = "SELECT * FROM Conversation WHERE category_id like "+str(category_id)+";"
    cursor.execute(sql)
    for row in cursor.fetchall():
        conversation_id = row[0]
        
    if(conversation_id):    
        sql = "DELETE FROM Conversation WHERE ID like "+str(conversation_id)+";"
        cursor.execute(sql)
    
        sql = "DELETE FROM ConversationTweets WHERE conversation_id like "+str(conversation_id)+"; "
        cursor.execute(sql)
        
        try:
            # Execute the SQL command
            cursor.execute(sql)
            # Commit your changes in the database
            db.commit()
        except Exception,e:
            # Rollback in case there is any error
            print "error on insertion of flushing source"
            print str(e)
            db.rollback()
                
        cursor.close()
    else:
        cursor.close()


def insertConversationForCategory(db, category_id, tweets):
    cursor = db.cursor()
    #identify representative tweet
    max_tweet = None
    for tweet in tweets:
        if(max_tweet == None) or (tweet["tweet_count"] > max_tweet["tweet_count"]):
            max_tweet = tweet
            
    
    sql = "INSERT INTO Conversation (category_id, representative_tweet) VALUES ("+str(category_id)+", '"
    sql += max_tweet["id"]+"');"
    try:
        # Execute the SQL command
        cursor.execute(sql)
        # Commit your changes in the database
        db.commit()
    except Exception,e:
        # Rollback in case there is any error
        print "error on insertion of flushing source"
        print str(e)
        db.rollback()
            
    conversation_id = cursor.lastrowid
    cursor.close()
    cursor = db.cursor()
    
    for tweet in tweets:
        sql = "INSERT INTO ConversationTweets (tweet_id, conversation_id) VALUE ('"
        sql += tweet["id"]+"', "+str(conversation_id)+");"
        try:
            # Execute the SQL command
            cursor.execute(sql)
            # Commit your changes in the database
            db.commit()
        except Exception,e:
            # Rollback in case there is any error
            print "error on insertion of flushing source"
            print str(e)
            db.rollback()
    
    cursor.close()
    
def getConversations(db):
    cursor = db.cursor()
    sql = "SELECT * From Conversation;"
    cursor.execute(sql)
    conversations = []
    for row in cursor.fetchall():
        conversation_id = row[0]
        representative_tweet = row[1]
        secondary_cursor = db.cursor()
        conversation = {}
        
        #get representative tweet
        secondary_cursor = db.cursor()
        sql = "SELECT text From Tweet WHERE twitter_id like "+str(representative_tweet)+";"
        secondary_cursor.execute(sql)
        for row in secondary_cursor.fetchall():
            conversation["representative_tweet"] = row[0]
        secondary_cursor.close()
        
        #get all children tweets
        secondary_cursor = db.cursor()
        sql = "SELECT * From ConversationTweets where conversation_id like "+str(conversation_id)+";"
        secondary_cursor.execute(sql)
        tweets = []
        for row in secondary_cursor.fetchall():
            tweet = {}
            third_cursor = db.cursor()
            sql = "SELECT text FROM Tweet WHERE twitter_id like '"+row[1]+"';"
            third_cursor.execute(sql)
            for row in third_cursor.fetchall():
                tweet["text"] = row[0]
                
            third_cursor.close()
            tweets.append(tweet)
        conversation["tweets"] = tweets
        secondary_cursor.close()
        conversations.append(conversation)
    
    cursor.close()
    return conversations





def addNewConversation(db, primary_tweet):
    cursor = db.cursor()
    sql = "INSERT INTO Conversation (representative_tweet) VALUES ("+primary_tweet["id"]+");"
    try:
        # Execute the SQL command
        cursor.execute(sql)
        # Commit your changes in the database
        db.commit()
    except Exception,e:
        # Rollback in case there is any error
        print "error on insertion of flushing source"
        print str(e)
        db.rollback()
    conversation_id = cursor.lastrowid
    cursor.close()
    return conversation_id

def addTweetToConversation(db, tweet, conversation_id):
    cursor = db.cursor()
    sql = "INSERT INTO ConversationTweets (tweet_id, conversation_id) VALUES ('"+tweet["id"]+"', "+str(conversation_id)+");"
    try:
        # Execute the SQL command
        cursor.execute(sql)
        # Commit your changes in the database
        db.commit()
    except Exception,e:
        # Rollback in case there is any error
        print "error on insertion of flushing source"
        print str(e)
        db.rollback()
    cursor.close()


def deleteConversationWithId(db, conversation_id):
    cursor = db.cursor()
    sql = "DELETE FROM ConversationTweets WHERE conversation_id like "+str(conversation_id)+";"
    try:
        # Execute the SQL command
        cursor.execute(sql)
        # Commit your changes in the database
        db.commit()
    except Exception,e:
        # Rollback in case there is any error
        print "error on insertion of flushing source"
        print str(e)
        db.rollback()
    cursor.close()
    
    
    cursor = db.cursor()
    sql = "DELETE FROM Conversation WHERE ID like "+str(conversation_id)+";"
    try:
        # Execute the SQL command
        cursor.execute(sql)
        # Commit your changes in the database
        db.commit()
    except Exception,e:
        # Rollback in case there is any error
        print "error on insertion of flushing source"
        print str(e)
        db.rollback()
    cursor.close()
    
    
    
    


        
    
    
    
    
    