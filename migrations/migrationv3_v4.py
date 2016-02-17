#This is a migration from 7a9e15e830e7b82856 to next commit
import MySQLdb

import sys
import re


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
        
        sql = "ALTER TABLE SourceCategoryRelationship ADD event_multiplier INT;"
        executeSql(db, sql)
        
        sql = "select table_name FROM information_schema.tables  WHERE table_name LIKE 'Occurrence_%';"
        cur = db.cursor()
        cur.execute(sql)
        rows = cur.fetchall()
        cur.close()
        for row in rows:
                sql = "ALTER TABLE "+str(row[0])+" ADD occurrence_value INT;"
                executeSql(db, sql)
        cur = db.cursor()
        sql = "select category_id,twitter_id, twitter_name from VoteHistory Group By twitter_handle, category_id ;"
        cur.execute(sql)
        rows = cur.fetchall()
        cur.close()
        for row in rows:
                sql = "INSERT INTO VoteHistory(category_id,twitter_id, twitter_name, value) VALUES('"+str(row[0])+"', '"+str(row[1])+"', '"+re.escape(row[2])+"', 19);"
                print sql
                executeSql(db, sql)
                
                
                
        print "Finished algorithm updates"
        
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
        
        print "Finished creating user"
        
        sql = "ALTER TABLE VoteHistory ADD user_id INT;"
        executeSql(db, sql)
        
        #find each unique ip address in VoteHistory
        sql = "SELECT DISTINCT ip_address from VoteHistory;"
        cursor = db.cursor()
        cursor.execute(sql)
        for row in cursor.fetchall():
                if(row[0] != None):
                        #ok we need to create a new user for each of these
                        if(row[0] == None):
                                sql = "INSERT INTO User (ip_address) VALUES (NULL);"
                        else:
                                sql = "INSERT INTO User (ip_address) VALUES ('"+row[0]+"');"
                                
                        print sql
                        new_id = executeSql(db, sql)
                        sql = "UPDATE VoteHistory set user_id="+str(new_id)+" WHERE ip_address like '"+row[0]+"';"
                        print sql
                        executeSql(db, sql)
                        
        cursor.close()
        
        print "Finished upating vote history to mvoe to user_id"
        
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
        print "Finished comment creation"
        
        sql = "CREATE TABLE CommentVoteHistory("
        sql += "ID int(11) NOT NULL PRIMARY KEY AUTO_INCREMENT, "
        sql += "comment_id int(11), "
        sql += "user_id int(11), "
        sql += "timestamp timestamp NULL DEFAULT CURRENT_TIMESTAMP, "
        sql += "value int(11), "
        sql += "FOREIGN KEY (comment_id) REFERENCES Comment(ID) ON DELETE CASCADE, "
        sql += "FOREIGN KEY (user_id) REFERENCES User(ID) ON DELETE CASCADE);"
        
        executeSql(db, sql)
        
        
        sql = "ALTER TABLE VoteHistory DROP COLUMN twitter_handle;"
        executeSql(db, sql)
        
        sql = "ALTER TABLE VoteHistory DROP COLUMN twitter_name;"
        executeSql(db, sql)
        
        sql = "ALTER TABLE VoteHistory ADD tweet_id INT;"
        executeSql(db, sql)
        
        
        
        print "Finished all"
        
    
    
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
        
        sql = "ALTER TABLE VoteHistory ADD twitter_handle varchar(255);"
        executeSql(db, sql)
        
        sql = "ALTER TABLE VoteHistory ADD twitter_name varchar(255);"
        executeSql(db, sql)
        
        sql = "ALTER TABLE VoteHistory DROP tweet_id;"
        executeSql(db, sql)
        
        sql = "SELECT twitter_id FROM VoteHistory"
        cursor = db.cursor()
        cursor.execute(sql)
        rows = cursor.fetchall()
        cursor.close()
        
        for row in rows:
                sql = "SELECT * From TwitterSource WHERE twitter_id like '"+str(row[0])+"';"
                print sql
                cursor = db.cursor()
                cursor.execute(sql)
                source = cursor.fetchone()
                cursor.close()
                twitter_name = source[1]
                twitter_handle = source[2]
                sql = "UPDATE VoteHistory SET twitter_name='"+re.escape(twitter_name)+"', twitter_handle='"+twitter_handle+"' WHERE twitter_id LIKE '"+str(row[0])+"';"
                executeSql(db, sql)
        
        sql = "Drop TABLE CommentVoteHistory;"
        executeSql(db, sql)
        
        sql = "Drop TABLE Comment;"
        executeSql(db, sql)
        
        sql = "ALTER TABLE VoteHistory ADD ip_address varchar(255);"
        executeSql(db, sql)
        
        sql = "SELECT ID, ip_address FROM User;"
        cursor = db.cursor()
        cursor.execute(sql)
        for row in cursor.fetchall():
                if(row[1] is not None):
                        sql = "UPDATE VoteHistory set ip_address='"+row[1]+"' WHERE user_id="+str(row[0])+";"
                        executeSql(db, sql)
                        
        cursor.close()
        
                
        
        sql = "Drop TABLE User;";
        executeSql(db, sql)
        
        sql = "ALTER TABLE VoteHistory DROP COLUMN user_id;"
        executeSql(db, sql)
        
        
        
        
        
        sql = "ALTER TABLE SourceCategoryRelationship DROP event_multiplier;"
        executeSql(db, sql)
        
        sql = "select table_name FROM information_schema.tables  WHERE table_name LIKE 'Occurrence_%';"
        cur = db.cursor()
        cur.execute(sql)
        rows = cur.fetchall()
        cur.close()
        for row in rows:
                sql = "ALTER TABLE "+str(row[0])+" DROP occurrence_value;"
                executeSql(db, sql)
                
        cur = db.cursor()
        sql = "DELETE FROM VoteHistory WHERE value>5;"
        executeSql(db, sql)
        
        
        