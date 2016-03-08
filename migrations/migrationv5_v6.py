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
        
        descendFromCategory(db, 109)
        
        
def descendFromCategory(db, cat_id):
        print "descending into cat: "+str(cat_id)
        processCategory(db, cat_id)
        sql = "SELECT child_category_id FROM CategoryParentRelationship WHERE parent_category_id="+str(cat_id)+";"
        cursor = db.cursor()
        cursor.execute(sql)
        rows = cursor.fetchall()
        cursor.close()
        for row in rows:
                descendFromCategory(db, row[0])

                
                
        
        
def processCategory(db, cat_id):
        print "processing for cat_id "+str(cat_id)
        sql = "SELECT source_twitter_id From SourceCategoryRelationship WHERE category_id="+str(cat_id)+";"
        cursor = db.cursor()
        cursor.execute(sql)
        handles = cursor.fetchall()
        cursor.close()
        for handle in handles:
                #must make sure this handle appears in all parents of this category
                insertIntoCategoryParents(db, handle[0], cat_id)
                
                
        
        
def insertIntoCategoryParents(db, twitter_id, cat_id):
        print "inserting "+str(twitter_id)+" into cat id: "+str(cat_id)
        sql = "SELECT parent_category_id From CategoryParentRelationship where child_category_id="+str(cat_id)+";"
        cursor = db.cursor()
        cursor.execute(sql)
        row = cursor.fetchone()
        cursor.close()
        #row[0] is the parent_id of the cat_id
        if(row is not None):
                ensureHandleInCategory(db, twitter_id, row[0] )
                insertIntoCategoryParents(db, twitter_id, row[0])
                
        
def ensureHandleInCategory(db, twitter_id, cat_id):
        #check if handle is in cat with cat id, if not add it
        sql = "SELECT ID From SourceCategoryRelationship WHERE source_twitter_id like '"+str(twitter_id)+"' AND category_id="+str(cat_id)+";"
        cursor = db.cursor()
        cursor.execute(sql)
        row = cursor.fetchone()
        cursor.close()
        if(row is None):
                #ok we need to insert 20 points into the Vote History
                sql = "INSERT INTO VoteHistory (category_id, twitter_id, value) VALUES ("+str(cat_id)+", '"+str(twitter_id)+"', 20);"
                print sql
                cursor = db.cursor()
                cursor.execute(sql)
                cursor.close()
                
        
        
        