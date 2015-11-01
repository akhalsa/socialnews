import untangle
import MySQLdb
import os
import tweepy
import re

class CategoryModel:
    
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
            self.insertCategory(cat, [])
            
        #clear db of any handles which were not in the document
        ########         SHOULD WIPE OUT ANY HANDLES WHICH ARE NO LONGER IN XML
        ##############################
            

    def insertCategory(self, category, parent_id_list):
        #1 create new category entry for this category
        sql = "INSERT INTO Category (name) values ('"+category['name']+"');"
        lastRow = str(self.executeSql(self.db, sql))
        category_chain = [lastRow]+parent_id_list
        
        #2.create a parent child relationship with the parent if there is one
        if (len(parent_id_list) > 1):
                sql = "INSERT INTO CategoryParentRelationship (parent_category_id, child_category_id) values ("+category_chain[1]+", "+lastRow+");"
                self.executeSql(self.db, sql)
        
        #insert all twitter handles into the db
        try:
            #make sure all handles in XML are also in DB
            for one_handle in category.handle:
                sql = "SELECT * From TwitterSource WHERE twitter_handle like '"+one_handle.cdata+"';"
                cursor = self.db.cursor()
                cursor.execute(sql)
                row = cursor.fetchone()
                if(row == None):
                    cursor.close()
                    user = self.api.get_user(screen_name = one_handle.cdata)
                    user_id = re.escape(str(user.id))
                    username = re.escape(user.name)
                    profile_link = user.profile_image_url
                    if(user_id is not False):
                        sql = "INSERT INTO TwitterSource(Name, twitter_handle, twitter_id, profile_image) VALUES ('"+username+"','"+one_handle.cdata+"', '"+user_id+"', '"+profile_link+"');"
                        print "will insert with: "+sql
                        self.executeSql(self.db, sql)
                else:
                    cursor.close()
                
                #insert source category mappings
                #for cat in category_chain:
                print "should insert "+one_handle.cdata+" for cats: "+str(category_chain)
            
            
            
            
        except IndexError, e:
            print "got exception: "+str(e)
            print "category: "+category['name']+" has no  handles"
            
        
        
        
        #3. call insertCategory for all child categories passing in the id of the current category object.
        try:
            for cat in category.category:
                self.insertCategory(cat, category_chain)
        except IndexError, e:
            print "category: "+category['name']+" has no children so were done"
