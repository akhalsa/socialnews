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
    
    sql = "CREATE TABLE VoteHistory (";
    sql += "ID int(11) NOT NULL AUTO_INCREMENT,"
    sql += "ip_address varchar(255) DEFAULT NULL,"
    sql += "category_id INT DEFAULT NULL,"
    sql += "twitter_id INT DEFAULT NULL,"
    sql += "twitter_handle varchar(255) DEFAULT NULL,"
    sql += "twitter_name varchar(255) DEFAULT NULL,"
    sql += "timestamp timestamp NULL DEFAULT CURRENT_TIMESTAMP,"
    sql += "value INT DEFAULT NULL,"
    sql += "PRIMARY KEY (ID), INDEX(timestamp));"
    executeSql(db, sql)
    print sql
    sql = "DROP TABLE SourceCategoryRelationship;"
    executeSql(db, sql)
    print sql
    
    
    
    
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

    sql = "DROP TABLE VoteHistory;";
    executeSql(db, sql)
    
    sql = "CREATE TABLE SourceCategoryRelationship ("
    sql += "ID int(11) NOT NULL AUTO_INCREMENT,"
    sql += "source_id int(11) DEFAULT NULL,"
    sql += "category_id int(11) DEFAULT NULL,"
    sql += "PRIMARY KEY (ID));"
    
    executeSql(db, sql)
    