import untangle
import MySQLdb
import os


define("port", default=8888, help="run on the given port", type=int)

db = MySQLdb.connect(
        host="avtar-news-db-2.cvnwfvvmmyi7.us-west-2.rds.amazonaws.com",
        user="akhalsa",
        passwd="sophiesChoice1",
        db="newsdb",
        charset='utf8',
        port=3306)



class CategoryModel:
    def __init__(self, db):
        print os.getcwd()
        obj = untangle.parse('handles.xml')
        #table naming scheme
        #GenCat0
        
        for cat in obj.root.category.category.category:
            print cat['name']
            for h in cat.handle:
                print h.cdata
