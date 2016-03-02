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
        
        #top level category: 109
        #what categories are we examining?
        parent_cat_id = 109
        all_children = get_child_cat_ids(109)
        print all_children
        
        
        
def get_child_cat_ids(cat_id):
        cursor = db.cursor()
        return_list = [cat_id]
        sql = "SELECT child_category_id From CategoryParentRelationship WHERE parent_category_id = "+str(cat_id)
        cursor.execute(sql)
        rows = cursor.fetchall()
        cursor.close()
        for row in rows:
                return_list.append(get_child_cat_ids(row[0]))

        return return_list
        
        
#         | VoteHistory | CREATE TABLE `VoteHistory` (
#   `ID` int(11) NOT NULL AUTO_INCREMENT,
#   `category_id` int(11) DEFAULT NULL,
#   `twitter_id` varchar(255) DEFAULT NULL,
#   `timestamp` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
#   `value` int(11) DEFAULT NULL,
#   `user_id` int(11) DEFAULT NULL,
#   `tweet_id` varchar(255) DEFAULT NULL,
#   PRIMARY KEY (`ID`),
#   KEY `timestamp` (`timestamp`)
# ) ENGINE=InnoDB AUTO_INCREMENT=3932 DEFAULT CHARSET=latin1 |
# 
#         
        
        
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
        
        ##no going back from this one :(
                
        
        
