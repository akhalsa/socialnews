import tornado.ioloop
import tornado.web
import tornado.websocket
import os, uuid
import socket   #for sockets
import sys  #for exit
import json
import MySQLdb
import tweepy
import thread
import urllib2
import threading
import datetime
import requests
import re
import urllib2

from tornado.options import define, options, parse_command_line
from threading import Thread
from Queue import Queue
import src.CategoryModel

define("port", default=8888, help="run on the given port", type=int)

        
def findCategoryChildrenForId(cat_id):
        lock.acquire()
        cursor = db.cursor()
        sql = "SELECT child_category_id From CategoryParentRelationship WHERE parent_category_id LIKE "+cat_id
        cursor.execute(sql)
        child_id_list = []
        for row in cursor.fetchall() :
                child_id_list.append(str(row[0]))
        cursor.close()
        
        cursor = db.cursor()
        return_list = []
        for id in child_id_list:
                sql = "SELECT Name From Category WHERE ID like "+id
                cursor.execute(sql)
                row = cursor.fetchone()
                return_list.append(str(row[0]))
        cursor.close()
        lock.release()
        return return_list

def findCategoryIdWithName(cat_name, local_db):
        cursor = local_db.cursor()
        sql = "SELECT ID FROM Category WHERE Name like '"+cat_name+"';"
        cursor.execute(sql)
        return_id = 0
        for row in cursor.fetchall() :
            return_id = row[0]
        cursor.close()
        return return_id

def getTweetOccurances(seconds, cat_id, local_db):
        cursor = local_db.cursor()

        #sql = "SELECT twitter_id as t_id, COUNT(twitter_id) as tweet_occurrence_count FROM TweetOccurrence WHERE timestamp > (NOW() -  INTERVAL "+ str(seconds)+" SECOND) AND category_id like "+str(cat_id)+" GROUP BY twitter_id ORDER BY tweet_occurrence_count DESC LIMIT 10;"
        sql = "SELECT twitter_id as t_id, COUNT(twitter_id) as tweet_occurrence_count FROM Occurrence_"+str(cat_id)+" WHERE timestamp > (NOW() -  INTERVAL "+ str(seconds)+" SECOND) GROUP BY twitter_id ORDER BY tweet_occurrence_count DESC LIMIT 10;"
        print "loading with sql: "+sql
        cursor.execute(sql)
        results = {}
        twitter_ids = []
        for row in cursor.fetchall():
                twitter_ids.append(row[0])
                results[row[0]] = {"tweet_count":row[1] }

        cursor.close()
        #add text
        if(len(twitter_ids)==0):
                return (results, twitter_ids)
        
        cursor = local_db.cursor()
        #sql = "SELECT twitter_id, text, source_id From Tweet A "
        #sql += "INNER JOIN (SELECT Name, profile_image, ID FROM TwitterSource) B "
        #sql += "ON A.source = A.source_id "
        #sql += "WHERE A.twitter_id in ("
        sql = "select Tweet.twitter_id, Tweet.text, TwitterSource.Name, TwitterSource.profile_image From Tweet Inner Join TwitterSource ON TwitterSource.ID = Tweet.source_id WHERE Tweet.twitter_id in ("
        first_fin = False
        for t_id in twitter_ids:
                if(first_fin == False):
                        first_fin = True
                else:
                        sql +=  ","
                        
                sql += t_id
                
        sql += ");"

        cursor.execute(sql)
        for row in cursor.fetchall():
                results[row[0]]["text"] = row[1]
                results[row[0]]["name"] = row[2]
                results[row[0]]["pic"] = row[3]
        cursor.close()
        print results
        return (results, twitter_ids)


class CategoryChildren(tornado.web.RequestHandler):
    def get(self, cat_label):
        local_db = MySQLdb.connect(
                host="avtar-news-db-2.cvnwfvvmmyi7.us-west-2.rds.amazonaws.com",
                user="akhalsa",
                passwd="sophiesChoice1",
                db="newsdb",
                charset='utf8',
                port=3306)
        cat_id = findCategoryIdWithName(cat_label, local_db)
        children = findCategoryChildrenForId(str(cat_id))
        return_dictionary = {"children":children}
        self.finish(json.dumps(return_dictionary))
        
class Category(tornado.web.RequestHandler):    
    def get(self, ):
        cur = db.cursor()
        cur.execute("SELECT * FROM Category")
        
        output_array = []
        for row in cur.fetchall():
            print ("appending: "+row[1])
            output_map = dict()
            output_map["Name"] = row[1]
            output_array.append(output_map)
        cur.close()
        self.finish(json.dumps(output_array))
    
class Reader(tornado.web.RequestHandler):
        def get(self, cat, time_frame_seconds):
                local_db = MySQLdb.connect(
                        host="avtar-news-db-2.cvnwfvvmmyi7.us-west-2.rds.amazonaws.com",
                        user="akhalsa",
                        passwd="sophiesChoice1",
                        db="newsdb",
                        charset='utf8',
                        port=3306)
                print "cat: "+cat
                print "seconds: "+time_frame_seconds
                cat_id = findCategoryIdWithName(cat, local_db)
                if(cat_id == 0):
                        self.finish("Category Error, Try Again")
                print "found category id: "+str(cat_id)        
                lookup = getTweetOccurances(time_frame_seconds, str(cat_id), local_db)
                self.finish(json.dumps(lookup[0]))
                
class PageLoad(tornado.web.RequestHandler):
        def get(self, url):
                print "********** ATTEMPTING TO ASYNC LOAD: "+url
                self.finish(urllib2.urlopen(url).read(200000))
                

app = tornado.web.Application([
    (r'/static/(.*)', tornado.web.StaticFileHandler, {"path": "./static"}),
    (r"/category", Category),
    (r"/category/(.*)", CategoryChildren),
    (r'/reader/(.*)/time/(.*)', Reader),
    (r'/page_load/(.*)',  PageLoad),
])

if __name__ == '__main__':
    
    parse_command_line()
    #db.query('SET GLOBAL wait_timeout=28800')
    
    
    print "done loading handles"
    app.listen(options.port)
    tornado.ioloop.IOLoop.instance().start()
    
    ####################
    #FIX SQL going away bug
    #http://stackoverflow.com/questions/207981/how-to-enable-mysql-client-auto-re-connect-with-mysqldb
    #####################