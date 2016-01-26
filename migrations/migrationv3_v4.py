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
        sql += "username varchar(255) NOT NULL, "
        sql += "password_hash varchar(255) NOT NULL, "
        sql += "email varchar(255) NOT NULL, "
        sql += "promotion_ip_address varchar(255), "
        sql += "UNIQUE INDEX (username), "
        sql += "UNIQUE INDEX (email)"
        sql += ");"
        executeSql(db, sql)
        
        sql = "ALTER TABLE VoteHistory ADD user_id varchar(255);"
        executeSql(db, sql)
        
        #find each unique ip address in VoteHistory
        sql = "SELECT DISTINCT ip_address from VoteHistory;"
        cursor = db.cursor()
        cursor.execute(sql)
        for row in cursor.fetchall():
                if(row[0] != None):
                        print row[0]

    
    
    
    
    
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

    sql = "Drop TABLE User;";
    executeSql(db, sql)
    
    sql = "ALTER TABLE VoteHistory DROP COLUMN user_id;"
    executeSql(db, sql)
    
    
