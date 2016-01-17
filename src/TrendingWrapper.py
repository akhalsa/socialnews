import MySQLdb


def clearConversationsForCategoryId(db, category_id):
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
    
    
    