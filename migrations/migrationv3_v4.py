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
        sql = "select * from VoteHistory Group By twitter_handle, category_id ;"
        cur.execute(sql)
        rows = cur.fetchall()
        cur.close()
        for row in rows:
                sql = "INSERT INTO VoteHistory(category_id,twitter_id, twitter_name, value) VALUES("+str(row[1])+", '"+str(row[2])+"', '"+row[3]+"', 19);"
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
        