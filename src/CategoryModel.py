import untangle
import MySQLdb
import os
import tweepy

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
    
    def __init__(self, db, api):
        
        self.db = db
        self.api = api

        # Execute the SQL command
        sql = "DELETE FROM CategoryParentRelationship;"
        self.executeSql(db,sql)
        sql = "ALTER TABLE CategoryParentRelationship AUTO_INCREMENT = 1"
        self.executeSql(db, sql)
        
        sql = "DELETE FROM Category;"
        self.executeSql(db, sql)
        sql = "ALTER TABLE Category AUTO_INCREMENT = 1"
        self.executeSql(db, sql)
        
        # sql = "DELETE FROM TwitterSource;"
        # self.executeSql(db, sql)
        # sql = "ALTER TABLE TwitterSource AUTO_INCREMENT = 1"
        # self.executeSql(db, sql)
        
        print os.getcwd()
        obj = untangle.parse('handles.xml')
        #table naming scheme
        #GenCat0
        for cat in obj.root.category:
            self.insertCategory(cat, self.top_level)
            

    def insertCategory(self, category, parent_id):
        #1 create new category entry for this category
        sql = "INSERT INTO Category (name) values ('"+category['name']+"');"
        lastRow = str(self.executeSql(self.db, sql))
        print "successful insert"
        
        #2.create a parent child relationship with the parent if there is one
        if (parent_id != self.top_level):
                sql = "INSERT INTO CategoryParentRelationship (parent_category_id, child_category_id) values ("+parent_id+", "+lastRow+");"
                self.executeSql(self.db, sql)
        
        #insert all twitter handles into the db
        try:
            for one_handle in category.handle:
                sql = "SELECT * From TwitterSource WHERE twitter_handle like '"+one_handle.cdata+"';"
                cursor = self.db.cursor()
                cursor.execute(sql)
                row = cursor.fetchone()
                if(row == None):
                    print "we need to do some processing for: "+one_handle.cdata
                
                
                # user = self.api.get_user(screen_name = one_handle.cdata)
                # user_id = str(user.id)
                # username = user.name
                # profile_link = user.profile_image_url
                # if(user_id is not False):
                #     sql = "INSERT INTO TwitterSource(Name, twitter_handle, twitter_id, profile_image) VALUES ('"+username+"','"+one_handle.cdata+"', '"+user_id+"', '"+profile_link+"');"
                #     self.executeSql(self.db, sql)
            
        except IndexError, e:
            print "got exception: "+str(e)
            print "category: "+category['name']+" has no  handles"
            
        
        
        
        #3. call insertCategory for all child categories passing in the id of the current category object.
        try:
            for cat in category.category:
                self.insertCategory(cat, lastRow)
        except IndexError, e:
            print "category: "+category['name']+" has no children so were done"
