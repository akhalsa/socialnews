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
    sql = "ALTER TABLE SourceCategoryRelationship CHANGE source_id source_twitter_id INT;"
    executeSql(db, sql)
    
    sql = "ALTER TABLE Tweet ADD COLUMN blurb varchar(255),"
    sql += " ADD COLUMN link_url varchar(255),"
    sql += " ADD COLUMN link_text varchar(255),"
    sql += " ADD COLUMN img_url varchar(255),"
    sql += " ADD COLUMN checked INT DEFAULT 0;"
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

    sql = "DROP TABLE VoteHistory;";
    executeSql(db, sql)
    
    sql = "ALTER TABLE SourceCategoryRelationship CHANGE source_twitter_id source_id INT;"
    executeSql(db, sql)
    
    sql = "ALTER TABLE Tweet DROP COLUMN blurb,"
    sql += " DROP COLUMN link_url,"
    sql += " DROP COLUMN link_text,"
    sql += " DROP COLUMN img_url,"
    sql += " DROP COLUMN checked;"
    executeSql(db, sql)
    
    # sql = "CREATE TABLE SourceCategoryRelationship ("
    # sql += "ID int(11) NOT NULL AUTO_INCREMENT,"
    # sql += "source_id int(11) DEFAULT NULL,"
    # sql += "category_id int(11) DEFAULT NULL,"
    # sql += "PRIMARY KEY (ID));"
    # 
    # 
    