#This is a migration from 7a9e15e830e7b82856 to next commit
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
        return lastRow
        
        
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
        
        
        sql = "CREATE TABLE User"
        sql += "(ID int(11) NOT NULL PRIMARY KEY AUTO_INCREMENT, "
        sql += "username varchar(255), "
        sql += "password_hash varchar(255), "
        sql += "email varchar(255), "
        sql += "ip_address varchar(255), "
        sql += "UNIQUE INDEX (username), "
        sql += "UNIQUE INDEX (email), "
        sql += "UNIQUE INDEX (ip_address)"
        sql += ");"
        executeSql(db, sql)
        
        sql = "ALTER TABLE VoteHistory ADD user_id INT;"
        executeSql(db, sql)
        
        #find each unique ip address in VoteHistory
        sql = "SELECT DISTINCT ip_address from VoteHistory;"
        cursor = db.cursor()
        cursor.execute(sql)
        for row in cursor.fetchall():
                if(row[0] != None):
                        #ok we need to create a new user for each of these
                        sql = "INSERT INTO User (ip_address) VALUES ('"+row[0]+"');"
                        new_id = executeSql(db, sql)
                        sql = "UPDATE VoteHistory set user_id="+str(new_id)+" WHERE ip_address like '"+row[0]+"';"
                        executeSql(db, sql)
                        
        cursor.close()
        sql = "ALTER TABLE VoteHistory DROP COLUMN ip_address;"
        executeSql(db, sql)
        
        sql = "CREATE TABLE Comment("
        sql += "ID int(11) NOT NULL PRIMARY KEY AUTO_INCREMENT, "
        sql += "user_id int(11), "
        sql += "text varchar(255), "
        sql += "timestamp timestamp NULL DEFAULT CURRENT_TIMESTAMP, "
        sql += "tweet_id int(11), "
        sql += "score int(11), "
        sql += "FOREIGN KEY (user_id) REFERENCES User(ID) ON DELETE CASCADE, "
        sql += "FOREIGN KEY (tweet_id) REFERENCES Tweet(ID) ON DELETE CASCADE);"
        
        
        executeSql(db, sql)
        
        sql = "CREATE TABLE CommentVoteHistory("
        sql += "ID int(11) NOT NULL PRIMARY KEY AUTO_INCREMENT, "
        sql += "comment_id int(11), "
        sql += "user_id int(11), "
        sql += "value int(11), "
        sql += "FOREIGN KEY (comment_id) REFERENCES Comment(ID) ON DELETE CASCADE, "
        sql += "FOREIGN KEY (user_id) REFERENCES User(ID) ON DELETE CASCADE);"
        
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
        
        sql = "Drop TABLE Comment;"
        executeSql(db, sql)
        
        sql = "Drop TABLE CommentVoteHistory;"
        executeSql(db, sql)
        
        sql = "ALTER TABLE VoteHistory ADD ip_address varchar(255);"
        executeSql(db, sql)
        
        sql = "SELECT ID, ip_address FROM User;"
        cursor = db.cursor()
        cursor.execute(sql)
        for row in cursor.fetchall():
                sql = "UPDATE VoteHistory set ip_address='"+row[1]+"' WHERE user_id="+str(row[0])+";"
                executeSql(db, sql)
        cursor.close()
        
                
        
        sql = "Drop TABLE User;";
        executeSql(db, sql)
        
        sql = "ALTER TABLE VoteHistory DROP COLUMN user_id;"
        executeSql(db, sql)
        
        
        
    
    
