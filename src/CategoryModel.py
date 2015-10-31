import untangle
import MySQLdb
import os


db = MySQLdb.connect(
        host="avtar-news-db-2.cvnwfvvmmyi7.us-west-2.rds.amazonaws.com",
        user="akhalsa",
        passwd="sophiesChoice1",
        db="newsdb",
        charset='utf8',
        port=3306)



class CategoryModel:
    def __init__(self, db):
        cursor = db.cursor()
        try:
                # Execute the SQL command
                sql = "DELETE FROM CategoryParentRelationship;"
                cursor.execute(sql)
                sql = "DELETE FROM Category;"
                cursor.execute(sql)
                # Commit your changes in the database
                db.commit()
        except Exception,e:
                # Rollback in case there is any error
                print "error on insertion of occurrence"
                print str(e)
                db.rollback()
        cursor.close()
        
        print os.getcwd()
        obj = untangle.parse('handles.xml')
        #table naming scheme
        #GenCat0
        
        for cat in obj.root.category.category.category:
            print cat['name']
            for h in cat.handle:
                print h.cdata