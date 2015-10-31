import untangle
import MySQLdb
import os


class CategoryModel:
    top_level = -1
    
    def executeSql(self, db, sql):
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
    
    def __init__(self, db):
        
        self.db = db

        # Execute the SQL command
        sql = "DELETE FROM CategoryParentRelationship;"
        self.executeSql(db,sql)        
        sql = "DELETE FROM Category;"
        self.executeSql(db, sql)
        
        print os.getcwd()
        obj = untangle.parse('handles.xml')
        #table naming scheme
        #GenCat0
        for cat in obj.root.category:
            self.insertCategory(cat, self.top_level)
            

        
        #for cat in obj.root.category.category.category:
        #    print cat['name']
        #    for h in cat.handle:
        #        print h.cdata
                
    def insertCategory(self, category, parent_id):
        #1 create new category entry for this category
        sql = "INSERT INTO Category (name) values ("+Category['name']+");"
        lastRow = str(self.executeSql(self.db, sql))
        
        #2.create a parent child relationship with the parent if there is one
        if (parent_id != self.top_level):
                sql = "INSERT INTO CategoryParentRelationship (parent_category_id, child_category_id) values ("+parent_id+", "+lastRow+");"
                self.executeSql(self.db, sql)
        
        #3. call insertCategory for all child categories passing in the id of the current category object.
        for cat in category.category:
                self.insertCategory(cat, lastRow)
        
        
        
        return