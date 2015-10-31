import untangle
import MySQLdb
import os


class CategoryModel:
    top_level = -1
    
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
        for cat in obj.root.category:
            insertCategory(cat, top_level)
            

        
        #for cat in obj.root.category.category.category:
        #    print cat['name']
        #    for h in cat.handle:
        #        print h.cdata
                
    def insertCategory(self, category, parent_id):
        #1 create new category entry for this category
        #2.create a parent child relationship with the parent if there is one
        #3. call insertCategory for all child categories passing in the id of the current category object.
        
        
        
        return