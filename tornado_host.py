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

define("mysql_host", default="0", help="Just need the end point", type=int)

host_live = "avtar-news-db-2.cvnwfvvmmyi7.us-west-2.rds.amazonaws.com"
host_dev = "avtar-news-db-dev.cvnwfvvmmyi7.us-west-2.rds.amazonaws.com"
host_target = host_live



class Category(tornado.web.RequestHandler):    
    def get(self, ):
        local_db = MySQLdb.connect(
                        host=host_target,
                        user="akhalsa",
                        passwd="sophiesChoice1",
                        db="newsdb",
                        charset='utf8',
                        port=3306)
        
        self.finish(json.dumps(getCategoryStructure(local_db)))

class HandleListForCategoryId(tornado.web.RequestHandler):
    def get(self, cat_id):
        local_db = MySQLdb.connect(
                        host=host_target,
                        user="akhalsa",
                        passwd="sophiesChoice1",
                        db="newsdb",
                        charset='utf8',
                        port=3306)
        
        #this should get the full list of handles and their scores in the category
        

class HandleVoteReceiver(tornado.web.RequestHandler):
    def post(self,twitter_id, category_id, positive  ):
        #first check to see if this ip address has been used more than 5 times
        local_db = MySQLdb.connect(
                        host=host_target,
                        user="akhalsa",
                        passwd="sophiesChoice1",
                        db="newsdb",
                        charset='utf8',
                        port=3306)
        
        votes_this_hour = getVoteCountByIpForTimeFrame(local_db, self.request.remote_ip, 3600)
        if(votes_this_hour > 5):
            self.finish("{'message':'you are out of votes, please wait for them to recharge}")
        
        #ok this ip address isnt throttled
        #lets add a vote
        
        insertVote(local_db, self.request.remote_ip, category_id, twitter_id, positive )
        
        self.finish("got source_id: "+source_id+" cat id:"+category_id+" positive: "+positive +" and ip address: "+self.request.remote_ip)
        
        
    
    

    
class Reader(tornado.web.RequestHandler):
        def get(self, cat, time_frame_seconds):
                local_db = MySQLdb.connect(
                        host=host_target,
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
    (r"/handle/(.*)/", HandleListForCategoryId),
    (r"/handle/(.*)/category_id/(.*)/upvote/(.*)", HandleVoteReceiver),
    (r"/category", Category),
    (r'/reader/(.*)/time/(.*)', Reader),
    (r'/page_load/(.*)',  PageLoad),
])

if __name__ == '__main__':
    
    
    parse_command_line()
    if(options.mysql_host == 0):
        host_target = host_live
    elif(options.mysql_host == 1):
        host_target = host_dev
        
    app.listen(options.port)
    tornado.ioloop.IOLoop.instance().start()
    
    ####################
    #FIX SQL going away bug
    #http://stackoverflow.com/questions/207981/how-to-enable-mysql-client-auto-re-connect-with-mysqldb
    #####################