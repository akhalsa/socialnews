from tornado.options import define, options, parse_command_line
from src.DBWrapper import *

define("mysql_host", default="0", help="Just need the end point", type=int)
define("cat_name", default="", help="Whats the new category called", type=str)
define("parent_cat_name", default="", help="Whats the parent category called", type=str)


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


def process(new_cat_name, parent_cat_name):
    db = MySQLdb.connect(
        host=host_target,
        user="akhalsa",
        passwd="sophiesChoice1",
        db="newsdb",
        charset='utf8',
        port=3306)
    
    if(new_cat_name == ""):
        print "you didn't supply a valid category name\n"
        return
    
    cat_id = findCategoryIdWithName(new_cat_name, db)
    if(cat_id != 0):
        print "you already nominated that category!"
        return
    
    parent_id = 0
    if(parent_cat_name != ""):
        parent_id = findCategoryIdWithName(parent_cat_name, db)
        if(parent_id == 0):
            print "invalid parent category name. BAIL!"
            return
    
    #ok were ready to insert the category
    sql = "INSERT INTO Category (name) values ('"+new_cat_name+"');"
    executeSql(db, sql)
    
    cat_id = findCategoryIdWithName(new_cat_name, db)
    
    if(parent_id != 0):
        sql = "INSERT INTO CategoryParentRelationship (parent_category_id, child_category_id) values ("+str(parent_id)+", "+str(cat_id)+");"
        executeSql(db, sql)



if __name__ == '__main__':
        
    parse_command_line()
    if(options.mysql_host == 0):
        host_target = host_live
    elif(options.mysql_host == 1):
        host_target = host_dev
    
    process(options.cat_name, options.parent_cat_name)
    
    
    
    
    