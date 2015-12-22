import untangle
import MySQLdb
import os
import re
import tweepy
from tornado.options import define, options, parse_command_line

auth = tweepy.OAuthHandler('pxtsR83wwf0xhKrLbitfIoo5l', 'Z12x1Y7KPRgb1YEWr7nF2UNrVbqEEctj4AiJYFR6J1hDQTXEQK')
auth.set_access_token('24662514-MCXJydvx0Mn5GWfW7RqQmXXsu35m8rNmzxKfHYJcM', 'f6zSrTomKIIr2c5zwcbkpbJYSpAZ2gi40yp57DEd86enN')
api = tweepy.API(auth)

define("mysql_host", default="0", help="Just need the end point", type=int)

host_live = "avtar-news-db-2.cvnwfvvmmyi7.us-west-2.rds.amazonaws.com"
host_dev = "avtar-news-db-dev.cvnwfvvmmyi7.us-west-2.rds.amazonaws.com"
host_target = host_live


class CategoryModel:
    
    categories = {}
    
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
                print sql
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
        
        sql = "DELETE FROM VoteHistory;"
        self.executeSql(db, sql)
        sql = "ALTER TABLE VoteHistory AUTO_INCREMENT = 1"
        self.executeSql(db, sql)
        
        sql = "DELETE FROM SourceCategoryRelationship;"
        self.executeSql(db, sql)
        sql = "ALTER TABLE SourceCategoryRelationship AUTO_INCREMENT = 1"
        self.executeSql(db, sql)
        
        sql = "DELETE FROM Tweet;"
        self.executeSql(db, sql)
        sql = "ALTER TABLE Tweet AUTO_INCREMENT = 1"
        self.executeSql(db, sql)
        
        #sql = "SELECT CONCAT( 'DROP TABLE ', GROUP_CONCAT(table_name) , ';' )  AS statement FROM information_schema.tables  WHERE table_name LIKE 'Occurrence_%';"
        sql = "select table_name FROM information_schema.tables  WHERE table_name LIKE 'Occurrence_%';"
        cur = db.cursor()
        cur.execute(sql)
        rows = cur.fetchall()
        cur.close()
        sql = "DROP TABLE "
        append_string = ""
        for row in rows:
            append_string += row[0]+", " 
            
        if(append_string != ""):
            sql += append_string
            print "delete with string: "+sql
            cur = db.cursor()
            cur.execute(sql)
            cur.close()
    

        self.executeSql(db, str(sql_to_run[0]))

        
        print os.getcwd()
        obj = untangle.parse('handles.xml')
        #table naming scheme
        #GenCat0
        for cat in obj.root.category:
            self.insertCategory(cat, [])
            
        #clear db of any handles which were not in the document
        ########         SHOULD WIPE OUT ANY HANDLES WHICH ARE NO LONGER IN XML
        ##############################
        
        ##############################
        ##### build category mapping
        ##############################
    #     ids = getAllTwitterIds(self.db)
    #     for handle_id in ids:
    #         local_info = findTableInfoWithTwitterId(handle_id, self.db)
    #         local_id = local_info["twitter_id"]
    #         
    #         cats = getCategoriesWithSourceId(local_id, self.db)
    #         self.categories[handle_id] = cats
    #         
    #     print "now have cats: "+str(self.categories)
    #     
    # def getCategoriesForTwitterUserId(self, handle_id):
    #     if(handle_id in self.categories):
    #         return self.categories[handle_id]
    #     else:
    #         return None
        
    def insertCategory(self, category, parent_id_list):
        #1 create new category entry for this category
        sql = "INSERT INTO Category (name) values ('"+category['name']+"');"
        lastRow = str(self.executeSql(self.db, sql))
        category_chain = [lastRow]+parent_id_list
        #2.create a parent child relationship with the parent if there is one
        if (len(category_chain) > 1):
                sql = "INSERT INTO CategoryParentRelationship (parent_category_id, child_category_id) values ("+category_chain[1]+", "+lastRow+");"
                self.executeSql(self.db, sql)
                
        #create occurrence table
        sql = "CREATE TABLE Occurrence_"+lastRow+"  (ID INT AUTO_INCREMENT PRIMARY KEY,twitter_id varchar(255), timestamp TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP, INDEX(timestamp));"
        self.executeSql(self.db, sql)
        
        #insert all twitter handles into the db
        try:
            #make sure all handles in XML are also in DB
            for one_handle in category.handle:
                category_id = lastRow
                
                sql = "SELECT * From TwitterSource WHERE twitter_handle like '"+one_handle.cdata+"';"
                cursor = self.db.cursor()
                cursor.execute(sql)
                row = cursor.fetchone()
                
                source_id = 0
                
                if(row == None):
                    cursor.close()
                    print "fetching data for: "+one_handle.cdata
                    user = self.api.get_user(screen_name = one_handle.cdata)
                    twitter_id = re.escape(str(user.id))
                    twitter_name = re.escape(user.name)
                    twitter_handle = one_handle.cdata
                    profile_link = user.profile_image_url
                    if(twitter_id is not False):
                        sql = "INSERT INTO TwitterSource(Name, twitter_handle, twitter_id, profile_image) VALUES ('"+twitter_name+"','"+twitter_handle+"', '"+twitter_id+"', '"+profile_link+"');"
                        source_id = self.executeSql(self.db, sql)
                     
                else:
                    source_id = row[0]
                    twitter_id = row[3]
                    twitter_handle = row[2]
                    twitter_name = re.escape(row[1])
                    cursor.close()
                    
                if(source_id != 0):
                    for cat_in_chain in category_chain:
                        sql = "INSERT INTO VoteHistory(category_id, twitter_id, twitter_handle, twitter_name, value) VALUES "
                        sql += "("+cat_in_chain+", '"+twitter_id+"', '"+twitter_handle+"', '"+twitter_name+"', 1);"
                        if(twitter_handle == "@RavensInsider"):
                            print sql
                        self.executeSql(self.db, sql)
                
                
                

        except IndexError, e:
            print "got exception: "+str(e)
            print "category: "+category['name']+" has no  handles"
            
        
        
        
        #3. call insertCategory for all child categories passing in the id of the current category object.
        try:
            for cat in category.category:
                self.insertCategory(cat, category_chain)
        except IndexError, e:
            print "category: "+category['name']+" has no children so were done"
            
            
if __name__ == '__main__':
    parse_command_line()
    if(options.mysql_host == 0):
        host_target = host_live
    elif(options.mysql_host == 1):
        host_target = host_dev
        
    db = MySQLdb.connect(
        host=host_target,
        user="akhalsa",
        passwd="sophiesChoice1",
        db="newsdb",
        charset='utf8',
        port=3306)
    
    mdl = CategoryModel(db, api)
        
    

