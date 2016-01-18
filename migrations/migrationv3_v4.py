#This is a migration from 4fe1904fd41f5377e3a9 to next commit
import MySQLdb

import sys



host_live = "avtar-news-db-2.cvnwfvvmmyi7.us-west-2.rds.amazonaws.com"
host_dev = "avtar-news-db-dev.cvnwfvvmmyi7.us-west-2.rds.amazonaws.com"
host_target = host_live

def executeSql(db, sql):
        cursor = db.cursor()
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
        lastRow = cursor.lastrowid
        cursor.close()
        
        
def forward():
    if(sys.argv[1] == "0"):
        host_target = host_live
    elif(sys.argv[1] == "1"):
        host_target = host_dev
    
    db = MySQLdb.connect(
        host=host_target,
        user="akhalsa",
        passwd="sophiesChoice1",
        db="newsdb",
        charset='utf8',
        port=3306)
    
    sql = "CREATE TABLE Conversation ("
    sql += "ID int(11) NOT NULL AUTO_INCREMENT, "
    sql += "category_id int(11), "
    sql += "representative_tweet varchar(255), "
    sql += "PRIMARY KEY (ID));"
    
    executeSql(db, sql)
    
    sql = "CREATE TABLE ConversationTweets ("
    sql += "ID int(11) NOT NULL AUTO_INCREMENT, "
    sql += "tweet_id varchar(255) NOT NULL, "
    sql += "conversation_id int(11) NOT NULL, "
    sql += "PRIMARY KEY (ID));"
    
    executeSql(db, sql)
    
    
    
def backward():
    if(sys.argv[1] == "0"):
        host_target = host_live
    elif(sys.argv[1] == "1"):
        host_target = host_dev
    
    db = MySQLdb.connect(
        host=host_target,
        user="akhalsa",
        passwd="sophiesChoice1",
        db="newsdb",
        charset='utf8',
        port=3306)


    
    sql = "DROP TABLE Conversation;"
    executeSql(db, sql)
    
    sql = "DROP TABLE ConversationTweets;"
    executeSql(db, sql)
    
    
    