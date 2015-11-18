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
import argparse


from tornado.options import define, options, parse_command_line
from threading import Thread
from Queue import Queue
from src.DBWrapper import *

import src.CategoryModel

define("port", default=8888, help="run on the given port", type=int)


class Category(tornado.web.RequestHandler):    
    def get(self, ):
        local_db = MySQLdb.connect(
                        host="avtar-news-db-2.cvnwfvvmmyi7.us-west-2.rds.amazonaws.com",
                        user="akhalsa",
                        passwd="sophiesChoice1",
                        db="newsdb",
                        charset='utf8',
                        port=3306)
        
        self.finish(json.dumps(getCategoryStructure(local_db)))
        

    
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
                self.finish(json.dumps(lookup))
                
class PageLoad(tornado.web.RequestHandler):
        def get(self, url):
                print "********** ATTEMPTING TO ASYNC LOAD: "+url
                self.finish(urllib2.urlopen(url).read(200000))
                
class IndexHandler(tornado.web.RequestHandler):
    @tornado.web.asynchronous
    def get(self):
        self.render("static/index.html")
        
app = tornado.web.Application([
    (r'/', IndexHandler),
    (r'/static/(.*)', tornado.web.StaticFileHandler, {"path": "./static"}),
    (r"/category", Category),
    (r'/reader/(.*)/time/(.*)', Reader),
    (r'/page_load/(.*)',  PageLoad),
])

if __name__ == '__main__':
    
    print "got host: "
    print host
    parse_command_line()
    app.listen(options.port)
    tornado.ioloop.IOLoop.instance().start()
    
    ####################
    #FIX SQL going away bug
    #http://stackoverflow.com/questions/207981/how-to-enable-mysql-client-auto-re-connect-with-mysqldb
    #####################